from flask import Flask, send_from_directory, jsonify, request, redirect, send_file
from config.conexao import conectar_banco
import psycopg2
import psycopg2.extras
import bcrypt
from fpdf import FPDF
import io
import os
from datetime import datetime

# Configuração do Flask para servir os arquivos do frontend que estão na pasta vizinha 'gestao'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'front')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

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
        cursor.execute("SELECT id, nome, cpf, cargo, setor, salario_base FROM funcionario")
        funcionarios = cursor.fetchall()

        processados = 0
        for f in funcionarios:
            # Busca soma de descontos para o funcionário
            cursor.execute("SELECT SUM(valor) as total FROM desconto WHERE id_funcionario = %s", (f['id'],))
            desc = cursor.fetchone()
            total_descontos = desc['total'] if desc['total'] else 0
            
            salario_bruto = float(f['salario_base'] or 0)
            salario_liquido = max(0, salario_bruto - float(total_descontos))

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
        pdf.cell(0, 10, f"Relatório de Folha de Pagamento - {mes:02d}/{ano}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Cabeçalho da Tabela
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(50, 10, "Funcionário", border=1)
        pdf.cell(30, 10, "CPF", border=1)
        pdf.cell(30, 10, "Cargo/Setor", border=1)
        pdf.cell(25, 10, "Salar. Bruto", border=1)
        pdf.cell(25, 10, "Descontos", border=1)
        pdf.cell(30, 10, "Salar. Líquido", border=1)
        pdf.ln()

        # Linhas de Dados
        pdf.set_font("helvetica", "", 8)
        for emp in pdf_list:
            pdf.cell(50, 10, str(emp['nome']), border=1)
            pdf.cell(30, 10, str(emp['cpf']), border=1)
            # Combina cargo e setor para otimizar o espaço no PDF
            info_func = f"{emp['cargo']} ({emp['setor']})"
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
        cursor.execute("SELECT salario_base FROM funcionario WHERE id = %s", (id_funcionario,))
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
            # Se a folha ainda não foi gerada pelo admin, calculamos em tempo real para a pré-visualização
            cursor.execute("SELECT SUM(valor) as total FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
            res_desc = cursor.fetchone()
            total_descontos = float(res_desc['total'] or 0)
            folha = {
                "salario_bruto": bruto_base,
                "descontos": total_descontos,
                "salario_liquido": max(0, bruto_base - total_descontos)
            }
        
        # Busca a lista detalhada de descontos para exibição no espaço abaixo
        cursor.execute("SELECT tipo as descricao, valor FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
        itens = cursor.fetchall()
        # Converte valores decimais para float para compatibilidade com JSON
        folha['itens_detalhados'] = [{"descricao": i['descricao'], "valor": float(i['valor'] or 0)} for i in itens]

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

    def safe_str(s): return str(s or "").encode('latin-1', 'replace').decode('latin-1')

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Busca dados do funcionário
        cursor.execute("SELECT nome, cpf, cargo, setor, salario_base FROM funcionario WHERE id = %s", (id_funcionario,))
        func = cursor.fetchone()
        if not func: return jsonify({"mensagem": "Funcionário não encontrado"}), 404
        
        # Busca dados da folha para o período
        cursor.execute("""
            SELECT salario_bruto, descontos, salario_liquido 
            FROM folha_pagamento 
            WHERE id_funcionario = %s AND mes = %s AND ano = %s
        """, (id_funcionario, mes_int, ano_int))
        folha = cursor.fetchone()

        if not folha:
            cursor.execute("SELECT SUM(valor) as total FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
            res_desc = cursor.fetchone()
            total_descontos = float(res_desc['total'] or 0)
            bruto = float(func.get('salario_base') or 0.0)
            folha = {
                "salario_bruto": bruto,
                "descontos": total_descontos,
                "salario_liquido": max(0, bruto - total_descontos)
            }
        
        # Busca detalhes de descontos (tabela rh_sistemas usa coluna 'tipo')
        cursor.execute("SELECT tipo as descricao, valor FROM desconto WHERE id_funcionario = %s", (id_funcionario,))
        descontos_itens = cursor.fetchall()

        # Gerar PDF
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
        pdf.cell(100, 8, "Salário Base", border=1)
        pdf.cell(45, 8, f"R$ {float(folha.get('salario_bruto') or 0):,.2f}", border=1, align="R")
        pdf.cell(45, 8, "-", border=1, align="R")
        pdf.ln()

        for item in descontos_itens:
            pdf.cell(100, 8, safe_str(item['descricao']), border=1)
            pdf.cell(45, 8, "-", border=1, align="R")
            pdf.cell(45, 8, f"R$ {float(item['valor'] or 0):,.2f}", border=1, align="R")
            pdf.ln()

        pdf.ln(5)
        pdf.set_text_color(164, 19, 60)
        pdf.cell(145, 8, safe_str("Líquido a Receber:"), align="R")
        pdf.cell(45, 8, f"R$ {float(folha.get('salario_liquido') or 0):,.2f}", align="R")

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
            SET nome = %s, cargo = %s, cpf = %s, setor = %s 
            WHERE id = %s
        """
        cursor.execute(query, (data.get('nome'), data.get('cargo'), data.get('cpf'), data.get('setor'), id_funcionario))
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
    senha = data.get('password')

    conn = conectar_banco()
    if not conn:
        return jsonify({"mensagem": "Erro de conexão com o servidor"}), 500

    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query_func = "INSERT INTO funcionario (nome, cpf, cargo, setor, data_admissao) VALUES (%s, %s, %s, %s, CURRENT_DATE) RETURNING id"
        cursor.execute(query_func, (nome, cpf, cargo, setor))
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

@app.route('/api/admin/funcionarios', methods=['GET'])
def listar_funcionarios():
    """Retorna a lista completa de funcionários cadastrados."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = "SELECT id, nome, cpf, cargo, setor, to_char(data_admissao, 'DD/MM/YYYY') as data_admissao FROM funcionario"
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
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
    """Retorna o histórico de ponto de todos os funcionários para o admin."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT f.nome, to_char(rp.data_registro, 'DD/MM/YYYY') as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo, 
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida 
            FROM registro_ponto rp JOIN funcionario f ON rp.id_funcionario = f.id 
            ORDER BY rp.data_registro DESC, rp.entrada DESC"""
        cursor.execute(query)
        return jsonify(cursor.fetchall()), 200
    finally:
        cursor.close()
        conn.close()

@app.route('/api/admin/relatorios/pdf', methods=['GET'])
def relatorio_geral_pdf():
    """Gera um PDF com o histórico de ponto de todos os funcionários."""
    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        query = """
            SELECT f.nome, to_char(rp.data_registro, 'DD/MM/YYYY') as data, 
                   rp.entrada, rp.saida_intervalo, rp.volta_intervalo, rp.saida 
            FROM registro_ponto rp
            JOIN funcionario f ON rp.id_funcionario = f.id
            ORDER BY rp.data_registro DESC, rp.entrada DESC
        """
        cursor.execute(query)
        registros = cursor.fetchall()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "Relatório Consolidado de Pontos por Dia", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

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
            pdf.cell(75, 8, str(r['nome']), border=1)
            pdf.cell(25, 8, str(r['entrada'] or '--:--'), border=1, align="C")
            pdf.cell(25, 8, str(r['saida_intervalo'] or '--:--'), border=1, align="C")
            pdf.cell(25, 8, str(r['volta_intervalo'] or '--:--'), border=1, align="C")
            pdf.cell(25, 8, str(r['saida'] or '--:--'), border=1, align="C")
            pdf.ln()

        pdf_bytes = pdf.output()
        # Garante compatibilidade de bytes para o envio do arquivo
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')
            
        return send_file(io.BytesIO(bytes(pdf_bytes)), mimetype="application/pdf", as_attachment=True, download_name=f"Relatorio_Por_Dia_{datetime.now().strftime('%d_%m_%Y')}.pdf")
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
        query = """
            SELECT COALESCE(to_char(rp.data_registro, 'DD/MM/YYYY'), to_char(rj.data_falta, 'DD/MM/YYYY')) as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo, 
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida,
                   j.tipo as just_tipo, rj.motivo as just_obs, rj.status as just_status
            FROM registro_ponto rp
            FULL OUTER JOIN registro_justificativa rj ON rp.id_funcionario = rj.id_funcionario 
                AND rp.data_registro = rj.data_falta
            LEFT JOIN justificativa j ON rj.id_funcionario = j.id_funcionario AND rj.data_falta = j.data_justificativa
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
        return jsonify(cursor.fetchall()), 200
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

        query = """
            SELECT COALESCE(to_char(rp.data_registro, 'DD/MM/YYYY'), to_char(rj.data_falta, 'DD/MM/YYYY')) as data, 
                   to_char(rp.entrada, 'HH24:MI') as entrada, to_char(rp.saida_intervalo, 'HH24:MI') as saida_intervalo, 
                   to_char(rp.volta_intervalo, 'HH24:MI') as volta_intervalo, to_char(rp.saida, 'HH24:MI') as saida,
                   j.tipo as just_tipo, rj.motivo as just_obs, rj.status as just_status
            FROM registro_ponto rp
            FULL OUTER JOIN registro_justificativa rj ON rp.id_funcionario = rj.id_funcionario 
                AND rp.data_registro = rj.data_falta
            LEFT JOIN justificativa j ON rj.id_funcionario = j.id_funcionario AND rj.data_falta = j.data_justificativa
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
                pdf.set_font("helvetica", "I", 8)
                pdf.cell(0, 8, f"   Justificativa ({r['just_tipo']} - Status: {r['just_status'] or 'Pendente'}): {r['just_obs'] or 'Sem observações'}", border='LRB', ln=True)
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

    conn = conectar_banco()
    if not conn: return jsonify({"mensagem": "Erro de conexão"}), 500
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Verifica se já existe um registro de ponto para este funcionário hoje
        cursor.execute("SELECT id FROM registro_ponto WHERE id_funcionario = %s AND data_registro = CURRENT_DATE", (id_func,))
        registro = cursor.fetchone()
        agora = datetime.now().strftime('%H:%M:%S')

        if registro:
            # Se já existe registro hoje, apenas atualiza a coluna específica (ex: almoço ou saída)
            cursor.execute(f"UPDATE registro_ponto SET {coluna} = %s WHERE id = %s", (agora, registro['id']))
        else:
            # Se é a primeira batida do dia (entrada), cria uma nova linha
            cursor.execute(f"INSERT INTO registro_ponto (id_funcionario, data_registro, {coluna}) VALUES (%s, CURRENT_DATE, %s)", (id_func, agora))
        
        conn.commit()
        return jsonify({"mensagem": f"{tipo} registrado com sucesso!", "horario": agora}), 200
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
        
        # 2. Presença Hoje (Percentual)
        cursor.execute("SELECT COUNT(DISTINCT id_funcionario) as presentes FROM registro_ponto WHERE data_registro = CURRENT_DATE")
        presentes = cursor.fetchone()['presentes']
        percent_presente = round((presentes / total_func * 100), 1) if total_func > 0 else 0
        
        # 3. Justificativas Pendentes
        cursor.execute("SELECT COUNT(*) as pendentes FROM registro_justificativa WHERE status = 'Pendente'")
        justificativas = cursor.fetchone()['pendentes']
        
        # 4. Atividade Recente (Últimos 5 registros)
        query_recente = """
            SELECT f.nome, to_char(rp.entrada, 'HH24:MI') as entrada, 
            to_char(rp.data_registro, 'DD/MM/YYYY') as data,
            CASE WHEN rp.entrada <= '08:05:00' THEN 'No Prazo' ELSE 'Atraso' END as status_ponto
            FROM registro_ponto rp
            JOIN funcionario f ON rp.id_funcionario = f.id
            ORDER BY rp.data_registro DESC, rp.entrada DESC
            LIMIT 5
        """
        cursor.execute(query_recente)
        atividades = cursor.fetchall()

        return jsonify({
            "total_funcionarios": total_func,
            "percent_presente": f"{percent_presente}%",
            "justificativas_pendentes": justificativas,
            "atividades": atividades
        })
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
        # quantidade_horas inicia em 0 até que seja aprovado/definido pelo admin
        cursor.execute(query_just, (id_funcionario, data_falta, tipo, motivo, horas_compensadas_bool, 0))

        conn.commit()
        return jsonify({"mensagem": "Justificativa enviada para análise!"}), 201
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"mensagem": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Rota para garantir que todos os arquivos (CSS, JS, Imagens) sejam encontrados
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print(f"\n--- Servidor High Control Point ---")
    print(f"Pasta do Frontend: {FRONTEND_DIR}")
    print(f"Acesse: http://localhost:5000\n")
    app.run(debug=True, port=5000)