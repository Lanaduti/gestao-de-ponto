from flask import Flask, send_from_directory, jsonify, request, redirect, send_file
import sys
from config.conexao import conectar_banco
import psycopg2
import psycopg2.extras
import bcrypt
from fpdf import FPDF
import io
import os
from datetime import datetime
import pytz

# Configuração do Flask para servir os arquivos do frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Adiciona o diretório pai ao path para permitir a importação de 'config'
sys.path.append(os.path.dirname(BASE_DIR))
FRONTEND_DIR = BASE_DIR
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

def safe_str(s):
    """Converte strings para latin-1 substituindo caracteres incompatíveis para evitar erros no FPDF."""
    if not s:
        return ""
    return str(s).encode('latin-1', 'replace').decode('latin-1')

def calcular_inss(salario):
    """Cálculo progressivo do INSS."""
    if salario <= 1518.00:
        return salario * 0.075
    elif salario <= 2793.88:
        return salario * 0.09
    elif salario <= 4190.83:
        return salario * 0.12
    else:
        return salario * 0.14

def get_employees_with_accumulated_delays(conn):
    """Retorna uma lista de funcionários com 2 ou mais dias de atraso."""
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    fuso_brasil = pytz.timezone("America/Sao_Paulo")
    hoje = datetime.now(fuso_brasil).date()

    query = """
        SELECT
            f.id,
            f.nome
        FROM
            funcionario f
        WHERE
            f.id IN (SELECT id_funcionario FROM registro_ponto WHERE data_registro = %s AND entrada > '08:05:00')
            AND f.id IN (SELECT id_funcionario FROM registro_ponto WHERE data_registro = %s - INTERVAL '1 day' AND entrada > '08:05:00')
    """
    cursor.execute(query, (hoje, hoje))
    return cursor.fetchall()

@app.route('/')
def index():
    """Serve o arquivo index.html principal como porta de entrada."""
    # Se não houver index.html, redireciona para a página de login
    if not os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return redirect('/pages/Login.html')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status')
def status_conexao():
    """Endpoint para verificar se o frontend consegue falar com o PostgreSQL via Python."""
    try:
        conn = conectar_banco()
        if conn:
            conn.close()
            return jsonify({"status": "online", "db": "PostgreSQL conectado com sucesso!"})
        return jsonify({"status": "erro", "mensagem": "Não foi possível conectar ao banco."}), 500
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Valida as credenciais no banco de dados."""
    data = request.json
    email = data.get('email')
    senha = data.get('password')

    conn = conectar_banco()
    if not conn:
        return jsonify({"mensagem": "Erro de conexão com o servidor"}), 500

    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Busca no usuário e traz os dados do funcionário vinculado
        # Removemos a senha do WHERE para validar via Python/Bcrypt
        query = """
            SELECT u.email, u.senha, u.tipo, u.id_funcionario, f.nome, f.cargo, f.setor, f.cpf, f.foto, 
                   f.salario_base, f.vale_transporte,
                   to_char(f.data_admissao, 'DD/MM/YYYY') as data_admissao 
            FROM usuario u
            LEFT JOIN funcionario f ON u.id_funcionario = f.id
            WHERE u.email = %s
        """
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        # Verifica se o usuário existe e se a senha (hash) é válida
        if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha'].encode('utf-8')):
            # Remove a senha do dicionário antes de enviar ao frontend por segurança
            user.pop('senha')
            # Converte Decimal para float para evitar erro de serialização JSON
            if user.get('salario_base') is not None:
                user['salario_base'] = float(user['salario_base'])

            # Verifica atrasos acumulados e alertas ativos para funcionários
            if user['tipo'] == 'funcionario':
                cursor.execute("SELECT valor FROM configuracao WHERE chave = 'alertas_atraso_ativo'")
                res_config = cursor.fetchone()
                alertas_ativos = res_config['valor'] == 'true' if res_config else False

                if alertas_ativos:
                    employees_with_accumulated_delays = get_employees_with_accumulated_delays(conn)
                    if any(emp['id'] == user['id_funcionario'] for emp in employees_with_accumulated_delays):
                        user['warning_message'] = "Atenção! Notamos que você já tem atrasos de dois dias. Tente chegar no horário para não ter desconto no seu salário."
            return jsonify(user), 200
        return jsonify({"mensagem": "E-mail ou senha incorretos. Acesso negado."}), 401
    except psycopg2.ProgrammingError as e:
        error_message = str(e)
        print(f"\n❌ ERRO DE PROGRAMAÇÃO SQL: {error_message}")
        if "doesn't exist" in error_message:
            return jsonify({"mensagem": "Erro: Estrutura de tabelas não encontrada. Verifique se criou 'usuario' e 'funcionario'."}), 500
        return jsonify({"mensagem": f"Erro de programação no banco: {error_message}"}), 500
    except Exception as e:
        print(f"\n❌ ERRO GERAL NA CONSULTA SQL: {e}")
        return jsonify({"mensagem": f"Erro interno ao consultar o banco de dados: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/admin/gerar-folha', methods=['POST'])
def gerar_folha_mensal():
    """Calcula a folha no banco e retorna um PDF com o relatório."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        hoje = datetime.now()
        mes, ano = hoje.month, hoje.year
        pdf_list = []

        # 1. Busca funcionários (incluindo nome para o PDF)
        cursor.execute("SELECT id, nome, cpf, cargo, setor, salario_base, vale_transporte FROM funcionario")
        funcionarios = cursor.fetchall()

        processados = 0
        for f in funcionarios:
            salario_bruto = float(f['salario_base'] or 0)
            
            # Cálculos Automáticos (INSS e VT)
            desc_inss = calcular_inss(salario_bruto)
            desc_vt = salario_bruto * 0.06 if f.get('vale_transporte') == 'S' else 0
            
            # Busca soma de descontos para o funcionário
            cursor.execute("SELECT SUM(valor) as total FROM desconto WHERE id_funcionario = %s", (f['id'],))
            desc = cursor.fetchone()
            total_manuais = float(desc['total'] or 0)
            
            total_descontos = desc_inss + desc_vt + total_manuais
            salario_liquido = max(0, salario_bruto - total_descontos)

            # 2. Insere ou atualiza a folha do mês
            query_folha = """
                INSERT INTO folha_pagamento (id_funcionario, mes, ano, salario_bruto, descontos, salario_liquido)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id_funcionario, mes, ano) DO UPDATE SET 
                salario_bruto=EXCLUDED.salario_bruto, 
                descontos=EXCLUDED.descontos, 
                salario_liquido=EXCLUDED.salario_liquido
            """
            cursor.execute(query_folha, (f['id'], mes, ano, salario_bruto, total_descontos, salario_liquido))
            
            pdf_list.append({
                "nome": f['nome'],
                "cpf": f['cpf'],
                "cargo": f['cargo'],
                "setor": f['setor'],
                "bruto": salario_bruto,
                "descontos": float(total_descontos),
                "liquido": salario_liquido
            })
            processados += 1

        conn.commit()

        # 3. Geração do PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, safe_str(f"Relatório de Folha de Pagamento - {mes:02d}/{ano}"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Cabeçalho da Tabela
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(50, 10, safe_str("Funcionário"), border=1)
        pdf.cell(30, 10, "CPF", border=1)
        pdf.cell(30, 10, "Cargo/Setor", border=1)
        pdf.cell(25, 10, safe_str("Salar. Bruto"), border=1)
        pdf.cell(25, 10, "Descontos", border=1)
        pdf.cell(30, 10, safe_str("Salar. Líquido"), border=1)
        pdf.ln()

        # Linhas de Dados
        pdf.set_font("helvetica", "", 8)
        for emp in pdf_list:
            pdf.cell(50, 10, safe_str(emp['nome']), border=1)
            pdf.cell(30, 10, str(emp['cpf']), border=1)
            # Combina cargo e setor para otimizar o espaço no PDF
            info_func = safe_str(f"{emp['cargo']} ({emp['setor']})")
            pdf.cell(30, 10, (info_func[:18] + '..') if len(info_func) > 20 else info_func, border=1)
            pdf.cell(25, 10, f"R$ {emp['bruto']:,.2f}", border=1)
            pdf.cell(25, 10, f"R$ {emp['descontos']:,.2f}", border=1)
            pdf.cell(30, 10, f"R$ {emp['liquido']:,.2f}", border=1)
            pdf.ln()

        pdf_bytes = pdf.output()
        # Garante que o conteúdo seja bytes para o send_file
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
            
        return send_file(io.BytesIO(bytes(pdf_bytes)), mimetype="application/pdf", as_attachment=True, download_name=f"Folha_{mes}_{ano}.pdf")

    except Exception as e:
        return jsonify({"mensagem": f"Erro ao gerar folha: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/contracheque/<int:id_funcionario>', methods=['GET'])
def buscar_contracheque(id_funcionario):
    """Busca os valores do contracheque para o funcionário e período selecionado."""
    mes = request.args.get('mes')
    ano = request.args.get('ano')
    
    # Se não passados, usa o mês atual
    hoje = datetime.now()
    if not mes or mes == 'undefined': mes = hoje.month
    if not ano or ano == 'undefined': ano = hoje.year

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Salário Bruto do cadastro original
        cursor.execute("SELECT salario_base, vale_transporte FROM funcionario WHERE id = %s", (id_funcionario,))
        func = cursor.fetchone()
        if not func: return jsonify({"mensagem": "Funcionário não encontrado"}), 404
        
        bruto_base = float(func['salario_base'] or 0)

        # Tenta buscar dados já processados na folha_pagamento
        cursor.execute("""
            SELECT salario_bruto, descontos, salario_liquido 
            FROM folha_pagamento 
            WHERE id_funcionario = %s AND mes = %s AND ano = %s
        """, (id_funcionario, mes, ano))
        folha = cursor.fetchone()

        if not folha:
            # Se a folha ainda não foi gerada, calculamos em tempo real
            desc_inss = calcular_inss(bruto_base)
            desc_vt = bruto_base * 0.06 if func.get('vale_transporte') == 'S' else 0
            
            cursor.execute("SELECT SUM(valor) as total FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
            res_desc = cursor.fetchone()
            total_manuais = float(res_desc['total'] or 0)
            
            total_descontos = desc_inss + desc_vt + total_manuais
            folha = {
                "salario_bruto": bruto_base,
                "descontos": total_descontos,
                "salario_liquido": max(0, bruto_base - total_descontos)
            }
        
        # Monta a lista detalhada de itens para o Frontend
        itens_detalhados = []
        itens_detalhados.append({"descricao": "INSS (Previdência)", "valor": calcular_inss(bruto_base)})
        if func.get('vale_transporte') == 'S':
            itens_detalhados.append({"descricao": "Vale Transporte (6%)", "valor": bruto_base * 0.06})

        cursor.execute("SELECT tipo as descricao, valor FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
        itens = cursor.fetchall()
        itens_detalhados.extend([{"descricao": i['descricao'], "valor": float(i['valor'] or 0)} for i in itens])

        folha['itens_detalhados'] = itens_detalhados

        return jsonify(folha), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/contracheque/pdf/<int:id_funcionario>', methods=['GET'])
def gerar_contracheque_pdf(id_funcionario):
    """Gera um PDF do contracheque para o funcionário e período selecionado."""
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    hoje = datetime.now()
    try:
        mes_int = int(mes) if mes and mes != 'undefined' else hoje.month
        ano_int = int(ano) if ano and ano != 'undefined' else hoje.year
    except ValueError:
        mes_int, ano_int = hoje.month, hoje.year

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Busca dados do funcionário
        cursor.execute("SELECT nome, cpf, cargo, setor, salario_base FROM funcionario WHERE id = %s", (id_funcionario,))
        func = cursor.fetchone()
        if not func: return jsonify({"mensagem": "Funcionário não encontrado"}), 404
        
        # Busca dados da folha para o período
        # Se a folha já foi gerada, usa os valores calculados
        cursor.execute("""
            SELECT salario_bruto, descontos, salario_liquido 
            FROM folha_pagamento 
            WHERE id_funcionario = %s AND mes = %s AND ano = %s
        """, (id_funcionario, mes_int, ano_int))
        folha = cursor.fetchone()
        
        salario_bruto_calc = float(func.get('salario_base') or 0.0)
        total_descontos_calc = 0.0
        salario_liquido_calc = 0.0

        # Se a folha não foi gerada, calcula em tempo real para o PDF
        if not folha:
            desc_inss = calcular_inss(salario_bruto_calc)
            desc_vt = salario_bruto_calc * 0.06 if func.get('vale_transporte') == 'S' else 0.0
            
            cursor.execute("SELECT COALESCE(SUM(valor), 0) as total FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
            total_manuais = float(cursor.fetchone()['total'])
            
            total_descontos_calc = desc_inss + desc_vt + total_manuais
            salario_liquido_calc = max(0, salario_bruto_calc - total_descontos_calc)
        else:
            salario_bruto_calc = float(folha['salario_bruto'])
            total_descontos_calc = float(folha['descontos'])
            salario_liquido_calc = float(folha['salario_liquido'])

        # Monta a lista detalhada de itens para o PDF
        itens_detalhados_pdf = []
        itens_detalhados_pdf.append({"descricao": "Salário Base", "vencimento": salario_bruto_calc, "desconto": 0.0})
        
        itens_detalhados_pdf.append({"descricao": "INSS (Previdência)", "vencimento": 0.0, "desconto": calcular_inss(salario_bruto_calc)})
        if func.get('vale_transporte') == 'S':
            itens_detalhados_pdf.append({"descricao": "Vale Transporte (6%)", "vencimento": 0.0, "desconto": salario_bruto_calc * 0.06})

        cursor.execute("SELECT tipo as descricao, valor FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
        manuais = cursor.fetchall()
        itens_detalhados_pdf.extend([{"descricao": m['descricao'], "vencimento": 0.0, "desconto": float(m['valor'] or 0)} for m in manuais])

        # Geração do PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, safe_str("CONTRACHEQUE - HIGH CONTROL POINT"), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"Referencia: {mes_int}/{ano_int}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 8, safe_str(f"Funcionário: {func['nome']}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, safe_str(f"CPF: {func['cpf']}"), new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, safe_str(f"Cargo: {func['cargo']} | Setor: {func['setor']}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Cabeçalho Tabela
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(100, 8, "Descrição", border=1)
        pdf.cell(45, 8, "Vencimentos", border=1, align="R")
        pdf.cell(45, 8, "Descontos", border=1, align="R")
        pdf.ln()
        pdf.set_font("helvetica", "", 10)
        for item in itens_detalhados_pdf:
            pdf.cell(100, 8, safe_str(item['descricao']), border=1)
            if item['vencimento'] > 0:
                pdf.cell(45, 8, f"R$ {item['vencimento']:,.2f}", border=1, align="R")
                pdf.cell(45, 8, "-", border=1, align="R")
            else:
                pdf.cell(45, 8, "-", border=1, align="R")
                pdf.cell(45, 8, f"R$ {item['desconto']:,.2f}", border=1, align="R")
            pdf.ln()

        pdf.ln(5)
        pdf.set_text_color(164, 19, 60)
        pdf.cell(145, 8, safe_str("Líquido a Receber:"), align="R")
        pdf.cell(45, 8, f"R$ {salario_liquido_calc:,.2f}", align="R")

        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1')
        return send_file(io.BytesIO(bytes(pdf_bytes)), mimetype="application/pdf", as_attachment=True, download_name=f"Contracheque_{mes_int}_{ano_int}.pdf")
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/alertas', methods=['GET'])
def buscar_alertas():
    """Busca funcionários que entraram após as 08:05 hoje."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Consideramos atraso qualquer entrada após 08:05:00 na data de hoje
        query = """
            SELECT f.nome, rp.entrada, to_char(rp.data_registro, 'DD/MM/YYYY') as data
            FROM registro_ponto rp
            JOIN funcionario f ON rp.id_funcionario = f.id
            WHERE rp.data_registro = CURRENT_DATE AND rp.entrada > '08:05:00'
        """
        cursor.execute(query)
        atrasos = cursor.fetchall()
        return jsonify(atrasos), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/perfil/atualizar', methods=['POST'])
def atualizar_perfil():
    """Atualiza os dados do funcionário no banco de dados."""
    data = request.json
    id_funcionario = data.get('id_funcionario')

    if not id_funcionario:
        return jsonify({"mensagem": "ID do funcionário não fornecido"}), 400

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500

    try:
        cursor = conn.cursor()
        query = """
            UPDATE funcionario 
            SET nome = %s, cargo = %s, cpf = %s, setor = %s, salario_base = %s, vale_transporte = %s
            WHERE id = %s
        """
        cursor.execute(query, (data.get('nome'), data.get('cargo'), data.get('cpf'), data.get('setor'), data.get('salario_base'), data.get('vale_transporte'), id_funcionario))
        conn.commit()
        return jsonify({"mensagem": "Perfil atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/perfil/foto', methods=['POST'])
def atualizar_foto():
    """Atualiza a foto do funcionário no banco de dados."""
    data = request.json
    id_funcionario = data.get('id_funcionario')
    foto = data.get('foto')  # String Base64 ou None

    if not id_funcionario:
        return jsonify({"mensagem": "ID do funcionário não fornecido"}), 400

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500

    try:
        cursor = conn.cursor()
        # Salva a string da imagem no banco de dados
        cursor.execute("UPDATE funcionario SET foto = %s WHERE id = %s", (foto, id_funcionario))
        conn.commit()
        return jsonify({"mensagem": "Foto de perfil atualizada!"}), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/cadastrar', methods=['POST'])
def cadastrar_funcionario():
    """Cadastra um novo funcionário e seu respectivo usuário."""
    data = request.json
    nome = data.get('nome')
    cpf = data.get('cpf')
    email = data.get('email')
    cargo = data.get('cargo')
    setor = data.get('setor')
    salario_base = data.get('salario_base', 0)
    vale_transporte = data.get('vale_transporte', 'N')
    senha = data.get('password')

    conn = conectar_banco()
    if not conn:
        return jsonify({"mensagem": "Erro de conexão com o servidor"}), 500

    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query_func = "INSERT INTO funcionario (nome, cpf, cargo, setor, salario_base, vale_transporte, data_admissao) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE) RETURNING id"
        cursor.execute(query_func, (nome, cpf, cargo, setor, salario_base, vale_transporte))
        id_funcionario = cursor.fetchone()['id']

        hashed_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query_user = "INSERT INTO usuario (email, senha, tipo, id_funcionario) VALUES (%s, %s, 'funcionario', %s)"
        cursor.execute(query_user, (email, hashed_senha, id_funcionario))

        conn.commit()
        return jsonify({"mensagem": "Funcionário cadastrado com sucesso!"}), 201
    except psycopg2.IntegrityError:
        return jsonify({"mensagem": "Erro: E-mail ou CPF já cadastrados."}), 400
    except Exception as e:
        return jsonify({"mensagem": f"Erro interno: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/admin/justificativas', methods=['GET'])
def listar_justificativas_admin():
    """Retorna todas as justificativas enviadas para o admin gerenciar."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT rj.id, f.nome, to_char(rj.data_falta, 'DD/MM/YYYY') as data,
                   rj.motivo, rj.status, rj.compensacao, 
                   (SELECT COALESCE(SUM(j.quantidade_horas), 0) 
                    FROM justificativa j 
                    WHERE j.id_funcionario = rj.id_funcionario 
                    AND j.data_justificativa::DATE = rj.data_falta::DATE) as horas
            FROM registro_justificativa rj
            JOIN funcionario f ON rj.id_funcionario = f.id
            ORDER BY CASE WHEN rj.status = 'Pendente' THEN 1 ELSE 2 END, rj.data_falta DESC, rj.id DESC
        """
        cursor.execute(query)
        justificativas = cursor.fetchall()
        # Converte Decimal para float para serialização JSON
        for j in justificativas:
            j['horas'] = float(j['horas'])
        return jsonify(justificativas), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/justificativas/status', methods=['POST'])
def atualizar_status_justificativa():
    """Aprova ou rejeita uma justificativa."""
    data = request.json
    id_just = data.get('id')
    novo_status = data.get('status')
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE registro_justificativa SET status = %s WHERE id = %s", (novo_status, id_just))
        conn.commit()
        return jsonify({"mensagem": f"Justificativa {novo_status} com sucesso!"}), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/funcionarios', methods=['GET'])
def listar_funcionarios():
    """Retorna a lista completa de funcionários cadastrados."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT id, nome, cpf, cargo, setor, salario_base, vale_transporte, to_char(data_admissao, 'DD/MM/YYYY') as data_admissao FROM funcionario"
        cursor.execute(query)
        funcionarios = cursor.fetchall()
        # Converte Decimal para float para evitar erro no jsonify
        for f in funcionarios:
            if f.get('salario_base') is not None:
                f['salario_base'] = float(f['salario_base'])
        return jsonify(funcionarios), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/excluir-funcionario/<int:id>', methods=['DELETE'])
def excluir_funcionario(id):
    """Exclui um funcionário e seu usuário vinculado do banco de dados."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    cursor = None
    try:
        cursor = conn.cursor()
        # 1. Remove o registro de acesso na tabela usuario
        cursor.execute("DELETE FROM usuario WHERE id_funcionario = %s", (id,))
        # 2. Remove o registro principal na tabela funcionario
        cursor.execute("DELETE FROM funcionario WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"mensagem": "Funcionário excluído com sucesso!"}), 200
    except psycopg2.IntegrityError:
        # Caso o funcionário tenha batidas de ponto ou outros registros vinculados
        return jsonify({"mensagem": "Erro: Não é possível excluir um funcionário que já possui registros de ponto ou folha ativos."}), 400
    except Exception as e:
        return jsonify({"mensagem": f"Erro interno: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/admin/relatorios', methods=['GET'])
def listar_relatorios_gerais():
    """Retorna o histórico de ponto de todos os funcionários para o admin com filtros de dia, mês e ano."""
    dia = request.args.get('dia')
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT f.nome, 
                   COALESCE(to_char(rp.data_registro, 'DD/MM/YYYY'), to_char(rj.data_falta, 'DD/MM/YYYY')) as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo, 
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida,
                   rj.motivo as just_obs, rj.status as just_status, rj.compensacao,
                   (SELECT COALESCE(SUM(j.quantidade_horas), 0) 
                    FROM justificativa j 
                    WHERE j.id_funcionario = rj.id_funcionario 
                    AND j.data_justificativa::DATE = rj.data_falta::DATE) as horas
            FROM registro_ponto rp 
            FULL OUTER JOIN registro_justificativa rj ON rp.id_funcionario = rj.id_funcionario AND rp.data_registro::DATE = rj.data_falta::DATE
            JOIN funcionario f ON COALESCE(rp.id_funcionario, rj.id_funcionario) = f.id
        """
        where_clauses = []
        params = []
        if dia:
            where_clauses.append("EXTRACT(DAY FROM COALESCE(rp.data_registro, rj.data_falta)) = %s")
            params.append(dia)
        if mes:
            where_clauses.append("EXTRACT(MONTH FROM COALESCE(rp.data_registro, rj.data_falta)) = %s")
            params.append(mes)
        if ano:
            where_clauses.append("EXTRACT(YEAR FROM COALESCE(rp.data_registro, rj.data_falta)) = %s")
            params.append(ano)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY COALESCE(rp.data_registro, rj.data_falta) DESC, f.nome ASC"
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()
        for r in registros:
            r['horas'] = float(r['horas']) if r.get('horas') is not None else 0.0
        return jsonify(registros), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/relatorios/pdf', methods=['GET'])
def relatorio_geral_pdf():
    """Gera um PDF consolidado com o histórico de ponto de todos os funcionários aplicando os filtros."""
    dia = request.args.get('dia')
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT f.nome, 
                   COALESCE(to_char(rp.data_registro, 'DD/MM/YYYY'), to_char(rj.data_falta, 'DD/MM/YYYY')) as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo, 
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida,
                   rj.motivo as just_obs, rj.status as just_status, rj.compensacao,
                   (SELECT COALESCE(SUM(j.quantidade_horas), 0) 
                    FROM justificativa j 
                    WHERE j.id_funcionario = rj.id_funcionario 
                    AND j.data_justificativa::DATE = rj.data_falta::DATE) as horas
            FROM registro_ponto rp
            FULL OUTER JOIN registro_justificativa rj ON rp.id_funcionario = rj.id_funcionario AND rp.data_registro::DATE = rj.data_falta::DATE
            JOIN funcionario f ON COALESCE(rp.id_funcionario, rj.id_funcionario) = f.id
        """
        where_clauses = []
        params = []
        if dia:
            where_clauses.append("EXTRACT(DAY FROM COALESCE(rp.data_registro, rj.data_falta)) = %s")
            params.append(dia)
        if mes:
            where_clauses.append("EXTRACT(MONTH FROM COALESCE(rp.data_registro, rj.data_falta)) = %s")
            params.append(mes)
        if ano:
            where_clauses.append("EXTRACT(YEAR FROM COALESCE(rp.data_registro, rj.data_falta)) = %s")
            params.append(ano)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY COALESCE(rp.data_registro, rj.data_falta) DESC, f.nome ASC"
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()

        # Título dinâmico para o PDF
        pdf_title = "Relatório Consolidado de Pontos"
        if dia and mes and ano:
            pdf_title = f"Relatório de Pontos - {dia}/{mes}/{ano}"
        elif mes and ano:
            meses_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            mes_str = meses_nome[int(mes)-1] if 1 <= int(mes) <= 12 else mes
            pdf_title = f"Relatório Mensal - {mes_str} de {ano}"

        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, pdf_title, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        download_name = f"Relatorio_Geral_{datetime.now().strftime('%d_%m_%Y')}.pdf"

        current_date = None

        for r in registros:
            # Se a data mudar, cria uma nova seção no PDF
            if r['data'] != current_date:
                current_date = r['data']
                
                # Adiciona um espaço extra antes de um novo dia (exceto no primeiro)
                pdf.ln(5)
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 8, f"DATA: {current_date}", border=1, ln=True, fill=True)
                
                # Cabeçalho da Tabela para o Dia
                pdf.set_font("helvetica", "B", 8)
                pdf.cell(75, 8, "Funcionário", border=1)
                pdf.cell(25, 8, "Entrada", border=1, align="C")
                pdf.cell(25, 8, "Almoço S.", border=1, align="C")
                pdf.cell(25, 8, "Almoço V.", border=1, align="C")
                pdf.cell(25, 8, "Saída", border=1, align="C")
                pdf.ln()

            # Linha do Funcionário
            pdf.set_font("helvetica", "", 8)
            pdf.cell(75, 8, safe_str(r['nome']), border=1)
            pdf.cell(25, 8, str(r['entrada'] or '--:--'), border=1, align="C")
            pdf.cell(25, 8, str(r['saida_intervalo'] or '--:--'), border=1, align="C")
            pdf.cell(25, 8, str(r['volta_intervalo'] or '--:--'), border=1, align="C")
            pdf.cell(25, 8, str(r['saida'] or '--:--'), border=1, align="C")
            pdf.ln()
            
            if r.get('just_obs'):
                pdf.set_font("helvetica", "I", 7)
                just_info = f"   Justificativa ({r['just_status'] or 'Pendente'}): {r['just_obs']}"
                if r.get('compensacao'):
                    just_info += f" | Compensar: {r['compensacao']}"
                
                horas_val = float(r.get('horas') or 0.0)
                if horas_val > 0:
                    just_info += f" ({horas_val}h)"
                
                pdf.cell(0, 6, safe_str(just_info), border='LRB', ln=True)
                pdf.set_font("helvetica", "", 8)

        pdf_bytes = pdf.output()
        # Garante compatibilidade de bytes para o envio do arquivo
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
            
        return send_file(io.BytesIO(bytes(pdf_bytes)), mimetype="application/pdf", as_attachment=True, download_name=download_name)
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/relatorios/<int:id_funcionario>', methods=['GET'])
def relatorio_funcionario(id_funcionario):
    """Retorna o histórico de ponto de um funcionário específico com filtros de mês e ano."""
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    # Garante que 'undefined' ou strings vazias não quebrem a lógica
    if not mes or mes == 'undefined': mes = None
    if not ano or ano == 'undefined': ano = None

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Busca o histórico unindo ponto, workflow de justificativa e detalhes da justificativa (horas)
        query = """
            SELECT COALESCE(to_char(rp.data_registro, 'DD/MM/YYYY'), to_char(rj.data_falta, 'DD/MM/YYYY')) as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo,
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida,
                   COALESCE(j.tipo, SPLIT_PART(rj.motivo, ']', 1)) as just_tipo, rj.motivo as just_obs, rj.status as just_status, rj.compensacao, COALESCE(j.quantidade_horas, 0) as horas
            FROM registro_ponto rp
            FULL OUTER JOIN registro_justificativa rj ON rp.id_funcionario = rj.id_funcionario 
                AND rp.data_registro::DATE = rj.data_falta::DATE
            LEFT JOIN justificativa j ON rj.id_funcionario = j.id_funcionario AND rj.data_falta::DATE = j.data_justificativa::DATE
            WHERE (rp.id_funcionario = %s OR rj.id_funcionario = %s)"""
        params = [id_funcionario, id_funcionario]

        if mes:
            query += " AND (EXTRACT(MONTH FROM rp.data_registro) = %s OR EXTRACT(MONTH FROM rj.data_falta) = %s)"
            params.extend([mes, mes])
        if ano:
            query += " AND (EXTRACT(YEAR FROM rp.data_registro) = %s OR EXTRACT(YEAR FROM rj.data_falta) = %s)"
            params.extend([ano, ano])

        query += " ORDER BY COALESCE(rp.data_registro, rj.data_falta) DESC"
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()
        # Converte Decimal para float para serialização JSON
        for r in registros:
            r['horas'] = float(r['horas']) if r.get('horas') is not None else 0.0
        return jsonify(registros), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/relatorios/pdf/<int:id_funcionario>', methods=['GET'])
def relatorio_funcionario_pdf(id_funcionario):
    """Gera um PDF com o histórico de ponto de um funcionário específico."""
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    # Garante que 'undefined' ou strings vazias não quebrem a lógica
    if not mes or mes == 'undefined': mes = None
    if not ano or ano == 'undefined': ano = None

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT nome FROM funcionario WHERE id = %s", (id_funcionario,))
        func = cursor.fetchone()
        if not func: return jsonify({"mensagem": "Funcionário não encontrado"}), 404
        func_nome = func['nome']

        # Query idêntica à do relatório JSON para manter consistência nas horas
        query = """
            SELECT COALESCE(to_char(rp.data_registro, 'DD/MM/YYYY'), to_char(rj.data_falta, 'DD/MM/YYYY')) as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo,
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida,
                   COALESCE(j.tipo, SPLIT_PART(rj.motivo, ']', 1)) as just_tipo, rj.motivo as just_obs, rj.status as just_status, rj.compensacao, COALESCE(j.quantidade_horas, 0) as horas
            FROM registro_ponto rp
            FULL OUTER JOIN registro_justificativa rj ON rp.id_funcionario = rj.id_funcionario 
                AND rp.data_registro::DATE = rj.data_falta::DATE
            LEFT JOIN justificativa j ON rj.id_funcionario = j.id_funcionario AND rj.data_falta::DATE = j.data_justificativa::DATE
            WHERE (rp.id_funcionario = %s OR rj.id_funcionario = %s)"""
        params = [id_funcionario, id_funcionario]
        if mes:
            query += " AND (EXTRACT(MONTH FROM rp.data_registro) = %s OR EXTRACT(MONTH FROM rj.data_falta) = %s)"
            params.extend([mes, mes])
        if ano:
            query += " AND (EXTRACT(YEAR FROM rp.data_registro) = %s OR EXTRACT(YEAR FROM rj.data_falta) = %s)"
            params.extend([ano, ano])

        query += " ORDER BY COALESCE(rp.data_registro, rj.data_falta) DESC"
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, f"Relatório de Ponto - {func_nome}", align="C", new_x="LMARGIN", new_y="NEXT")
        
        if mes and ano:
            meses_extenso = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            mes_nome = meses_extenso[int(mes)-1] if 1 <= int(mes) <= 12 else "Inválido"
            pdf.set_font("helvetica", "I", 12)
            pdf.cell(0, 10, f"Mês: {mes_nome} de {ano}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        pdf.set_font("helvetica", "B", 10)
        pdf.cell(35, 10, "Data", border=1, align="C")
        pdf.cell(35, 10, "Entrada", border=1, align="C")
        pdf.cell(40, 10, "Almoço S.", border=1, align="C")
        pdf.cell(40, 10, "Almoço V.", border=1, align="C")
        pdf.cell(35, 10, "Saída", border=1, align="C")
        pdf.ln()

        pdf.set_font("helvetica", "", 10)
        for r in registros:
            pdf.cell(35, 10, str(r['data']), border=1, align="C")
            pdf.cell(35, 10, str(r['entrada'] or '--:--'), border=1, align="C")
            pdf.cell(40, 10, str(r['saida_intervalo'] or '--:--'), border=1, align="C")
            pdf.cell(40, 10, str(r['volta_intervalo'] or '--:--'), border=1, align="C")
            pdf.cell(35, 10, str(r['saida'] or '--:--'), border=1, align="C")
            pdf.ln()
            
            if r.get('just_tipo'):
                just_hours_str = f" ({float(r['horas'] or 0.0)}h justificadas)" if float(r['horas'] or 0.0) > 0 else ""
                just_info = f"   Justificativa ({r['just_tipo']} - Status: {r['just_status'] or 'Pendente'}): {r['just_obs'] or 'Sem observações'}"
                if r.get('compensacao'):
                    just_info += f" | Compensar: {r['compensacao']}"
                just_info += just_hours_str
                
                pdf.set_font("helvetica", "I", 8)
                pdf.cell(0, 8, safe_str(just_info), border='LRB', ln=True)
                pdf.set_font("helvetica", "", 10)

        pdf_bytes = pdf.output()
        # Garante que o conteúdo seja bytes para o send_file em qualquer versão do fpdf
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
            
        return send_file(io.BytesIO(bytes(pdf_bytes)), mimetype="application/pdf", as_attachment=True, download_name=f"Relatorio_{func_nome}.pdf")

    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/ponto/status/<int:id_funcionario>', methods=['GET'])
def status_ponto(id_funcionario):
    """Retorna as batidas realizadas pelo funcionário no dia de hoje."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT to_char(entrada, 'HH24:MI') as entrada, 
                   to_char(saida_intervalo, 'HH24:MI') as saida_intervalo, 
                   to_char(volta_intervalo, 'HH24:MI') as volta_intervalo, 
                   to_char(saida, 'HH24:MI') as saida 
            FROM registro_ponto 
            WHERE id_funcionario = %s AND data_registro = CURRENT_DATE
        """
        cursor.execute(query, (id_funcionario,))
        status = cursor.fetchone()
        return jsonify(status if status else {}), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/ponto/registrar', methods=['POST'])
def registrar_ponto_api():
    """Registra ou atualiza uma batida de ponto para o dia atual."""
    data = request.json
    id_func = data.get('id_funcionario')
    tipo = data.get('tipo')

    # Mapeia o texto do select para a coluna exata no banco de dados
    mapeamento = {
        "Entrada": "entrada",
        "Sair para o intervalo": "saida_intervalo",
        "Volta do intervalo": "volta_intervalo",
        "Saída": "saida"
    }
    coluna = mapeamento.get(tipo)
    if not coluna: return jsonify({"mensagem": "Tipo de batida inválido"}), 400

    # Whitelist para evitar qualquer manipulação de coluna na query
    if coluna not in ["entrada", "saida_intervalo", "volta_intervalo", "saida"]:
        return jsonify({"mensagem": "Coluna inválida"}), 400

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        fuso_brasil = pytz.timezone("America/Sao_Paulo")
        agora_dt = datetime.now(fuso_brasil)
        hoje = agora_dt.date()
        agora_time = agora_dt.strftime('%H:%M:%S')

        # Verifica se já existe um registro de ponto para este funcionário hoje
        cursor.execute("SELECT id FROM registro_ponto WHERE id_funcionario = %s AND data_registro = %s", (id_func, hoje))
        registro = cursor.fetchone()

        # Verifica se a coluna já possui um valor para o dia atual
        if registro and registro.get(coluna) is not None:
            return jsonify({"mensagem": f"Você já registrou a {tipo} hoje às {registro[coluna]}. Não é possível registrar novamente."}), 400


        if registro:
            # Se já existe registro hoje, apenas atualiza a coluna específica (ex: almoço ou saída)
            cursor.execute(f"UPDATE registro_ponto SET {coluna} = %s WHERE id = %s", (agora_time, registro['id']))
        else:
            # Se é a primeira batida do dia (entrada), cria uma nova linha
            cursor.execute(f"INSERT INTO registro_ponto (id_funcionario, data_registro, {coluna}) VALUES (%s, %s, %s)", (id_func, hoje, agora_time))
        
        conn.commit()
        return jsonify({"mensagem": f"{tipo} registrado com sucesso!", "horario": agora_time}), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/dashboard-stats')
def dashboard_stats():
    """Retorna estatísticas consolidadas e atividades recentes para o Dashboard."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 1. Total de Funcionários
        cursor.execute("SELECT COUNT(*) as total FROM funcionario")
        total_func = cursor.fetchone()['total']
        
        # 2. Presença e Atrasos Hoje
        cursor.execute("SELECT COUNT(DISTINCT id_funcionario) as presentes FROM registro_ponto WHERE data_registro = CURRENT_DATE")
        presentes = cursor.fetchone()['presentes']
        percent_presente = round((presentes / total_func * 100), 1) if total_func > 0 else 0

        cursor.execute("SELECT COUNT(DISTINCT id_funcionario) as atrasados FROM registro_ponto WHERE data_registro = CURRENT_DATE AND entrada > '08:05:00'")
        atrasados_hoje = cursor.fetchone()['atrasados']
        
        # 3. Justificativas Pendentes
        cursor.execute("SELECT COUNT(*) as pendentes FROM registro_justificativa WHERE status = 'Pendente'")
        justificativas = cursor.fetchone()['pendentes']
        
        # 4. Atividade Recente (Últimos 5 registros do dia atual)
        query_recente = """
            SELECT f.nome, to_char(rp.entrada, 'HH24:MI') as entrada, 
            to_char(rp.data_registro, 'DD/MM/YYYY') as data,
            CASE WHEN rp.entrada <= '08:05:00' THEN 'No Prazo' ELSE 'Atraso' END as status_ponto
            FROM registro_ponto rp
            JOIN funcionario f ON rp.id_funcionario = f.id
            WHERE rp.data_registro = CURRENT_DATE
            ORDER BY rp.entrada DESC
            LIMIT 5
        """
        cursor.execute(query_recente)
        atividades = cursor.fetchall()

        # 5. Status Global de Alertas
        cursor.execute("SELECT valor FROM configuracao WHERE chave = 'alertas_atraso_ativo'")
        res_config = cursor.fetchone()
        alertas_ativos = res_config['valor'] == 'true' if res_config else False

        # 6. Funcionários com Atrasos Acumulados
        employees_with_accumulated_delays = get_employees_with_accumulated_delays(conn)

        return jsonify({
            "total_funcionarios": presentes,
            "percent_presente": f"{percent_presente}%",
            "total_atrasados_hoje": atrasados_hoje,
            "total_alertas_acumulados": len(employees_with_accumulated_delays),
            "justificativas_pendentes": justificativas,
            "atividades": atividades,
            "alertas_ativos": alertas_ativos,
            "employees_with_accumulated_delays": employees_with_accumulated_delays
        }), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/justificativa/registrar', methods=['POST'])
def registrar_justificativa():
    """Registra uma nova justificativa sincronizando as tabelas registro_justificativa e justificativa."""
    data = request.json
    id_funcionario = data.get('id_funcionario') # id_funcionario
    tipo = data.get('tipo') # tipo
    data_falta = data.get('data_falta') # data_falta
    motivo = data.get('motivo') # motivo
    compensacao = data.get('compensacao', 'Não') # compensacao
    horas_compensadas_bool = True if compensacao == 'Sim' else False
    
    # Captura a quantidade de horas do frontend, se enviada
    quantidade_horas_req = data.get('quantidade_horas', 0)
    try:
        quantidade_horas_req = float(quantidade_horas_req)
    except (ValueError, TypeError):
        quantidade_horas_req = 0.0
    final_quantidade_horas = quantidade_horas_req # Salva as horas sempre que enviadas

    if not all([id_funcionario, tipo, data_falta, motivo]):
        return jsonify({"mensagem": "Dados incompletos para registrar justificativa."}), 400

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        
        # IMPORTANTE: Proteção contra sessão inválida ou ID nulo
        if not id_funcionario or id_funcionario == 'null':
            return jsonify({"mensagem": "Funcionário não identificado na sessão. Faça login novamente."}), 401

        # Lógica: Concatenar o 'tipo' no 'motivo' para a tabela registro_justificativa
        # conforme solicitado, salvando no campo 'motivo' do banco rh_sistemas
        motivo_com_tipo = f"[{tipo}] {motivo}"

        # 1. Registro na tabela registro_justificativa (Focada em Workflow/Status)
        query_reg = """ 
            INSERT INTO registro_justificativa (id_funcionario, data_falta, motivo, status, compensacao)
            VALUES (%s, %s, %s, 'Pendente', %s)
        """
        cursor.execute(query_reg, (id_funcionario, data_falta, motivo_com_tipo, compensacao))

        # 2. Registro na tabela justificativa (Focada em Histórico e Impacto)
        query_just = """
            INSERT INTO justificativa (id_funcionario, data_justificativa, tipo, descricao, horas_compensadas, quantidade_horas)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_just, (id_funcionario, data_falta, tipo, motivo, horas_compensadas_bool, final_quantidade_horas))

        conn.commit()
        return jsonify({"mensagem": "Justificativa enviada para análise!"}), 201
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/forgot-password/verify-cpf', methods=['POST'])
def verify_cpf_for_reset():
    """Verifica se o CPF está cadastrado e vinculado a um usuário para redefinição de senha."""
    data = request.json
    cpf = data.get('cpf')

    if not cpf:
        return jsonify({"mensagem": "CPF não fornecido."}), 400

    conn = conectar_banco()
    if not conn:
        return jsonify({"mensagem": "Erro de conexão com o servidor"}), 500

    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Busca o funcionário ignorando formatação (pontos e traços) no banco de dados
        sql = "SELECT id FROM funcionario WHERE REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s"
        cursor.execute(sql, (cpf,))
        funcionario = cursor.fetchone()

        if not funcionario:
            return jsonify({"mensagem": "CPF não encontrado."}), 404

        id_funcionario = funcionario['id']

        # Verifica se existe um usuário vinculado a este funcionário
        cursor.execute("SELECT id FROM usuario WHERE id_funcionario = %s", (id_funcionario,))
        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({"mensagem": "Nenhum usuário vinculado a este CPF."}), 404

        return jsonify({"mensagem": "CPF verificado com sucesso!", "id_funcionario": id_funcionario}), 200
    except Exception as e:
        print(f"\n❌ ERRO AO VERIFICAR CPF: {e}")
        return jsonify({"mensagem": f"Erro interno ao verificar CPF: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/api/forgot-password/reset-password', methods=['POST'])
def reset_password():
    """Redefine a senha de um usuário com base no CPF."""
    data = request.json
    cpf = data.get('cpf')
    new_password = data.get('new_password')

    if not cpf or not new_password:
        return jsonify({"mensagem": "CPF e nova senha são obrigatórios."}), 400

    conn = conectar_banco()
    if not conn:
        return jsonify({"mensagem": "Erro de conexão com o servidor"}), 500

    cursor = None
    try:
        cursor = conn.cursor()
        # Busca o ID comparando apenas os números
        sql_id = "SELECT id FROM funcionario WHERE REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s"
        cursor.execute(sql_id, (cpf,))
        funcionario = cursor.fetchone()
        if not funcionario:
            return jsonify({"mensagem": "CPF não encontrado."}), 404

        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE usuario SET senha = %s WHERE id_funcionario = %s", (hashed_password, funcionario[0]))
        conn.commit()
        return jsonify({"mensagem": "Senha redefinida com sucesso!"}), 200
    except Exception as e:
        return jsonify({"mensagem": f"Erro ao redefinir senha: {str(e)}"}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Rota para garantir que todos os arquivos (CSS, JS, Imagens) sejam encontrados
@app.route('/api/config/alertas', methods=['GET'])
def obter_config_alertas():
    """Retorna se o sistema de alertas de atraso está ativado."""
    conn = conectar_banco()
    if not conn: return jsonify({"ativo": False}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM configuracao WHERE chave = 'alertas_atraso_ativo'")
        res = cursor.fetchone()
        ativo = res[0] == 'true' if res else False
        return jsonify({"ativo": ativo}), 200
    finally:
        conn.close()

@app.route('/api/admin/config/alertas', methods=['POST'])
def salvar_config_alertas():
    """Ativa ou desativa os alertas de atraso (Apenas Admin)."""
    data = request.json
    ativo = 'true' if data.get('ativo') else 'false'
    
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO configuracao (chave, valor) 
            VALUES ('alertas_atraso_ativo', %s) 
            ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor
        """, (ativo,))
        conn.commit()
        return jsonify({"mensagem": "Configuração de alertas atualizada!"}), 200
    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
    finally:
        conn.close()

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print(f"\n--- Servidor High Control Point ---")
    print(f"Pasta do Frontend: {FRONTEND_DIR}")
    print(f"Acesse: http://localhost:5000\n")
    app.run(debug=True, port=5000)
        return jsonify({"mensagem": str(e)}), 500
    finally:
        conn.close()

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print(f"\n--- Servidor High Control Point ---")
    print(f"Pasta do Frontend: {FRONTEND_DIR}")
    print(f"Acesse: http://localhost:5000\n")
    app.run(debug=True, port=5000)