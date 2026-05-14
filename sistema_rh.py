import urllib.request
import json
from funcionario import Funcionario
from fpdf import FPDF
from conexao import conectar_banco
from datetime import datetime, date, timezone, timedelta


class SistemaRH:
    def __init__(self):
        pass

    def cadastrar_funcionario(
        self, nome, cpf, cargo, setor, salario_base, vale_transporte, data_admissao
    ):
        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()
                
                # VERIFICA SE O CPF JÁ EXISTE
                cursor.execute(
                    "SELECT id FROM funcionario WHERE cpf = %s",
                    (cpf,)
                )

                cpf_existente = cursor.fetchone()

                if cpf_existente:
                    print("ERRO: Já existe um funcionário cadastrado com esse CPF!")
                    return False

                sql = """
                    INSERT INTO funcionario ( nome, cpf, cargo, setor, salario_base, vale_transporte, data_admissao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id 
                """
                valores = (nome, cpf, cargo, setor, salario_base, vale_transporte, data_admissao)
                cursor.execute(sql, valores)
                id_gerado = cursor.fetchone()[0]
                conn.commit()
                print(
                    f" Funcionário(a) '{nome}' cadastrado(a) com sucesso no Banco de Dados!"
                )
                cursor.close()
                return id_gerado

            except Exception as e:
                print(f" Erro ao cadastrar no banco: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        else:
            print("Não foi possível conectar ao banco para realizar o cadastro.")
            return False

    def listar_funcionarios(self):
        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()
                sql = "SELECT id, nome, cpf, cargo, setor, salario_base, data_admissao FROM funcionario"
                cursor.execute(sql)

                resultados = cursor.fetchall()

                print("\n---  Lista de Funcionários (Direto do Banco de Dados) ---")

                if not resultados:
                    print("Nenhum funcionário cadastrado no momento.")
                else:
                    for linha in resultados:
                        print(
                            f"ID: {linha[0]:02d} | Nome: {linha[1]:<15} | Cargo: {linha[3]:<20} | Admissão: {linha[6]}"
                        )

                print("-" * 65)

                cursor.close()
            except Exception as e:
                print(f" Erro ao buscar dados no banco: {e}")
            finally:
                conn.close()
        else:
            print("Sem conexão com o banco de dados.")

    def editar_funcionario(
        self,
        id_funcionario,
        nome,
        cpf,
        cargo,
        setor,
        salario_base
    ):

        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()

            # VERIFICA SE O CPF JÁ EXISTE EM OUTRO FUNCIONÁRIO
                cursor.execute(
                    """
                    SELECT id FROM funcionario
                    WHERE cpf = %s AND id != %s
                    """,
                    (cpf, id_funcionario)
                )

                cpf_existente = cursor.fetchone()

                if cpf_existente:
                    print("ERRO: CPF já cadastrado em outro funcionário!")
                    return

                sql = """
                    UPDATE funcionario
                    SET nome = %s,
                        cpf = %s,
                        cargo = %s,
                        setor = %s,
                        salario_base = %s
                    WHERE id = %s
                """

                cursor.execute(
                    sql,
                    (
                        nome,
                        cpf,
                        cargo,
                        setor,
                        salario_base,
                        id_funcionario
                    )
                )

                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Funcionário ID {id_funcionario} atualizado com sucesso!")

                else:
                    print("Funcionário não encontrado.")

                cursor.close()

            except Exception as e:
                print(f"Erro ao editar funcionário: {e}")
                conn.rollback()

            finally:
                conn.close()

    def excluir_funcionario(self, id_funcionario):

        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()

                sql = "DELETE FROM funcionario WHERE id = %s"

                cursor.execute(sql, (id_funcionario,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Funcionário ID {id_funcionario} excluído com sucesso!")

                else:
                    print("Funcionário não encontrado.")

                cursor.close()

            except Exception as e:
                print(f"Erro ao excluir funcionário: {e}")
                conn.rollback()

            finally:
                conn.close()

    # 22/04/2026 Victor adicionando FR02 (Função criar usuário e função de login)
    def cadastrar_usuario(self, email, senha, tipo, id_funcionario):
        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO usuario (email, senha, tipo, id_funcionario)
                    VALUES (%s, %s, %s, %s)
                    """
                cursor.execute(sql, (email, senha, tipo, id_funcionario))
                conn.commit()
                print(f"Usuário de acesso '{email}' criado com sucesso!")
                cursor.close()
                return True
            except Exception as e:
                print(f"Erro ao criar usuário de acesso: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()

# Função responsável pela autenticação do usuário
    def login(self, email, senha):
        conn = conectar_banco()
        
        if conn:
            try:
                
                cursor = conn.cursor()
                
                sql = """
                    SELECT id, email, tipo, id_funcionario
                    FROM usuario
                    WHERE email = %s AND senha = %s
                    """
                cursor.execute(sql, (email, senha))
                
                usuario = cursor.fetchone()
                
                if usuario:
                    return {
                        
                        "id": usuario[0],
                        "email": usuario[1],
                        "tipo": usuario[2],
                        "id_funcionario": usuario[3],
                        
                        }
                else:
                    print("\nEMAIL OU SENHA INCORRETOS!")
                    return None
                
            except Exception as e:
                print(f"Erro no login: {e}")
                return None
            
            finally:
                
                conn.close()

    # 29/04/2026 Victor adicionando FR06 calculando horas trabalhadas.
    def calcular_horas_trabalhadas(self, id_funcionario, data_calculo):
        """Calcula as horas trabalhadas no dia descontando o intervalo."""
        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()
                sql = """
                    SELECT entrada, saida_intervalo, volta_intervalo, saida
                    FROM registro_ponto
                    WHERE id_funcionario = %s AND data_registro = %s
                    """
                cursor.execute(sql, (id_funcionario, data_calculo))
                registro = cursor.fetchone()

                if not registro:
                    print(f"NENHUM ponto registrado para a data {data_calculo}.")
                    return None

                entrada, s_int, v_int, saida = registro

                if None in (entrada, s_int, v_int, saida):
                    print(
                        "A jornada de hoje ainda não terminou! Faltam batidas de ponto para fechar o calculo."
                    )
                    return None

                data_base = date.today()

                dt_entrada = datetime.combine(data_base, entrada)
                dt_s_int = datetime.combine(data_base, s_int)
                dt_v_int = datetime.combine(data_base, v_int)
                dt_saida = datetime.combine(data_base, saida)

                tempo_total_empresa = dt_saida - dt_entrada
                tempo_intervalo = dt_v_int - dt_s_int

                horas_efetivas = tempo_total_empresa - tempo_intervalo

                print(f"-- Fechamento do Dia ({data_calculo})---")
                print(f"Tempo total na empresa: {tempo_total_empresa}")
                print(f"Tempo de intervalo...: {tempo_intervalo}")
                print(f"Horas trabalhadas...: {horas_efetivas}")
                print("-" * 38)

                cursor.close()
                return horas_efetivas

            except Exception as e:
                print(f"Erro ao calcular horas: {e}")
            finally:
                conn.close()

    def gerar_contracheque(self, id_funcionario):

        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()

                sql = """
                    SELECT nome, cargo, salario_base, vale_transporte
                    FROM funcionario
                    WHERE id = %s
                """

                cursor.execute(sql, (id_funcionario,))
                funcionario = cursor.fetchone()

                if not funcionario:
                    print("Funcionário não encontrado.")
                    return

                nome = funcionario[0]
                cargo = funcionario[1]
                salario_base = float(funcionario[2])
                vale_transporte = funcionario[3]

            # DESCONTO VT
                desconto_vt = 0

                if vale_transporte == "S":
                    desconto_vt = salario_base * 0.06

            # INSS SIMPLES
                desconto_inss = salario_base * 0.08

                salario_liquido = (
                    salario_base
                    - desconto_vt
                    - desconto_inss
                )

                print("\n===== CONTRACHEQUE =====")
                print(f"Funcionário: {nome}")
                print(f"Cargo: {cargo}")

                print(f"\nSalário Base: R$ {salario_base:.2f}")
                print(f"Desconto VT: R$ {desconto_vt:.2f}")
                print(f"INSS: R$ {desconto_inss:.2f}")

                print("-" * 30)

                print(f"SALÁRIO LÍQUIDO: R$ {salario_liquido:.2f}")

                cursor.close()

            except Exception as e:
                print(f"Erro ao gerar contracheque: {e}")

            finally:
                conn.close()
  
    def registrar_ponto(self, id_funcionario):

        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()

                agora = datetime.now().time()
                hoje = date.today()

            # VERIFICA SE JÁ EXISTE REGISTRO HOJE
                cursor.execute("""
                    SELECT id FROM registro_ponto
                    WHERE id_funcionario = %s AND data_registro = %s
                """, (id_funcionario, hoje))

                registro = cursor.fetchone()

                if not registro:
                # PRIMEIRA BATIDA (ENTRADA)
                    cursor.execute("""
                        INSERT INTO registro_ponto
                        (id_funcionario, data_registro, entrada)
                        VALUES (%s, %s, %s)
                    """, (id_funcionario, hoje, agora))

                    print("Entrada registrada com sucesso!")

                else:
                # ATUALIZA CICLO DO DIA
                    cursor.execute("""
                        SELECT entrada, saida_intervalo, volta_intervalo, saida
                        FROM registro_ponto
                        WHERE id_funcionario = %s AND data_registro = %s
                    """, (id_funcionario, hoje))

                    ponto = cursor.fetchone()

                    if ponto[0] and not ponto[1]:
                        cursor.execute("""
                            UPDATE registro_ponto
                            SET saida_intervalo = %s
                            WHERE id_funcionario = %s AND data_registro = %s
                        """, (agora, id_funcionario, hoje))
                        print("Saída para intervalo registrada!")

                    elif ponto[1] and not ponto[2]:
                          cursor.execute("""
                              UPDATE registro_ponto
                              SET volta_intervalo = %s
                              WHERE id_funcionario = %s AND data_registro = %s
                          """, (agora, id_funcionario, hoje))
                          print("Volta do intervalo registrada!")

                    elif ponto[2] and not ponto[3]:
                          
                          cursor.execute("""
                              UPDATE registro_ponto
                              SET saida = %s
                              WHERE id_funcionario = %s AND data_registro = %s
                          """, (agora, id_funcionario, hoje))
                          print("Saída final registrada!")
                    else:
                        print("Todos os pontos do dia já foram registrados!")

                conn.commit()
                cursor.close()

            except Exception as e:
                print(f"Erro ao registrar ponto: {e}")
                conn.rollback()

            finally:
                conn.close()

    def exportar_relatorio_pdf(self, id_funcionario, mes, ano):
        """Gera um arquivo PDF com o relatório de ponto do mês."""
        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT nome, cpf FROM funcionario WHERE id = %s", (id_funcionario,)
                )
                func = cursor.fetchone()

                if not func:
                    print("Funcionário não encontrado no Banco de Dados.")
                    return

                nome_func, cpf_func = func

                sql = """
                    SELECT data_registro, entrada, saida_intervalo,volta_intervalo, saida
                    FROM registro_ponto 
                    WHERE id_funcionario = %s
                        AND EXTRACT(MONTH FROM data_registro) = %s
                        AND EXTRACT(YEAR FROM data_registro) = %s
                        ORDER BY data_registro ASC
                """
                cursor.execute(sql, (id_funcionario, mes, ano))
                registros = cursor.fetchall()

                if not registros:
                    print("Nenhum registro encontrado para gerar o PDF neste período.")
                    return

                # --- COMEÇANDO A DESENHAR O PDF ---
                pdf = FPDF()
                pdf.add_page()

                # Título Principal (Usando helvetica em Negrito 'B')
                pdf.set_font("helvetica", "B", 16)
                pdf.cell(190, 10, txt="Relatorio de Ponto Mensal", ln=True, align="C")

                # Informações do Funcionário (Usando helvetica normal)
                pdf.set_font("helvetica", size=12)
                pdf.cell(
                    190,
                    10,
                    txt=f"Funcionario: {nome_func} | CPF: {cpf_func}",
                    ln=True,
                    align="L",
                )
                pdf.cell(190, 10, txt=f"Periodo: {mes:02d}/{ano}", ln=True, align="L")
                pdf.ln(5)  # Pula uma linha

                # Cabeçalho da Tabela
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(30, 10, "Data", border=1, align="C")
                pdf.cell(35, 10, "Entrada", border=1, align="C")
                pdf.cell(35, 10, "Saida Int.", border=1, align="C")
                pdf.cell(35, 10, "Volta Int.", border=1, align="C")
                pdf.cell(35, 10, "Saida", border=1, align="C")
                pdf.ln()

                # Preenchendo as linhas da tabela com os dados do banco
                pdf.set_font("helvetica", size=10)
                for reg in registros:
                    data_formatada = reg[0].strftime("%d/%m/%Y")
                    entrada = str(reg[1]) if reg[1] else "---"
                    saida_int = str(reg[2]) if reg[2] else "---"
                    volta_int = str(reg[3]) if reg[3] else "---"
                    saida = str(reg[4]) if reg[4] else "---"

                    pdf.cell(30, 10, data_formatada, border=1, align="C")
                    pdf.cell(35, 10, entrada, border=1, align="C")
                    pdf.cell(35, 10, saida_int, border=1, align="C")
                    pdf.cell(35, 10, volta_int, border=1, align="C")
                    pdf.cell(35, 10, saida, border=1, align="C")
                    pdf.ln()

                nome_arquivo = (
                    f"Relatorio_Ponto_{nome_func.replace(' ', '_')}_{mes:02d}_{ano}.pdf"
                )
                pdf.output(nome_arquivo)

                print(
                    f"\n SUCESSO! O arquivo '{nome_arquivo}' foi criado na pasta do projeto."
                )

            except Exception as e:
                print(f" Erro ao gerar PDF: {e}")
            finally:
                cursor.close()
                conn.close()

    # 02/05/2026 Victor adicionando RF09 (O sistema deve permitir que o funcionário envie justificativas.)
    def enviar_justificativa(self, id_funcionario, data_falta, motivo, compensacao):
        """Salva uma justificativa com a opção de compensação de horas."""
        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS registro_justificativa (
                        id SERIAL PRIMARY KEY,
                        id_funcionario INTEGER REFERENCES funcionario(id),
                        data_falta DATE,
                        motivo TEXT,
                        status VARCHAR(20) DEFAULT 'Pendente',
                        data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()

                try:
                    cursor.execute(
                        "ALTER TABLE registro_justificativa ADD COLUMN compensacao VARCHAR(3) DEFAULT 'Não'"
                    )
                    conn.commit()
                except Exception:
                    conn.rollback()

                sql = "INSERT INTO registro_justificativa (id_funcionario, data_falta, motivo, compensacao) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (id_funcionario, data_falta, motivo, compensacao))
                conn.commit()

                print(f"\n SUCESSO! Justificativa enviada para a análise do RH.")
                print(f"Status: PENDENTE | Compensar horas: {compensacao}")

                cursor.close()
            except Exception as e:
                print(f" Erro ao enviar justificativa: {e}")
                conn.rollback()
            finally:
                conn.close()

    def listar_justificativas(self):

        conn = conectar_banco()

        if conn:
            try:
               cursor = conn.cursor()

               sql = """
                   SELECT
                       rj.id,
                       f.nome,
                       rj.data_falta,
                       rj.motivo,
                       rj.compensacao,
                       rj.status
                    FROM registro_justificativa rj
                    JOIN funcionario f
                    ON rj.id_funcionario = f.id
                    ORDER BY rj.data_envio DESC
                """

               cursor.execute(sql)

               justificativas = cursor.fetchall()

               print("\n--- JUSTIFICATIVAS ---")

               if not justificativas:
                   print("Nenhuma justificativa encontrada.")

               else:
                   for j in justificativas:
                       print(
                           f"""
    ID: {j[0]}
    Funcionário: {j[1]}
    Data: {j[2]}
    Motivo: {j[3]}
    Compensação: {j[4]}
    Status: {j[5]}
    -------------------------
    """
                        )

               cursor.close()

            except Exception as e:
                print(f"Erro ao listar justificativas: {e}")

            finally:
                conn.close()

    def atualizar_status_justificativa(self, id_justificativa, status):

        conn = conectar_banco()

        if conn:
            try:
                cursor = conn.cursor()

                sql = """
                    UPDATE registro_justificativa
                    SET status = %s
                    WHERE id = %s
                """

                cursor.execute(sql, (status, id_justificativa))

                conn.commit()

                if cursor.rowcount > 0:
                    print("Status atualizado com sucesso!")

                else:
                    print("Justificativa não encontrada.")

                cursor.close()

            except Exception as e:
                print(f"Erro ao atualizar justificativa: {e}")
                conn.rollback()

            finally:
                conn.close()

    def verificar_admin(self, email, senha):
    # ADMIN FIXO DO SISTEMA      
        if email == "admin@point.comm" and senha == "admin@123":
            return True

        return False

        # aqui é onde vão ficar as funções relacionados a manipulações de dados tipo cadastro e essas paradas fechouuuuuu??
