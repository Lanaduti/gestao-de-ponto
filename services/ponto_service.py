import pytz
from conexao import conectar_banco
from datetime import datetime, date



def registrar_ponto(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            fuso_brasil = pytz.timezone("America/Sao_Paulo")

            agora_brasilia = datetime.now(fuso_brasil)

            agora = agora_brasilia.time()

            hoje = date.today()

            cursor.execute("""
                SELECT id
                FROM registro_ponto
                WHERE id_funcionario = %s
                AND data_registro = %s
            """, (id_funcionario, hoje))

            registro = cursor.fetchone()
            
            if not registro:

                cursor.execute("""
                    INSERT INTO registro_ponto
                    (
                        id_funcionario,
                        data_registro,
                        entrada
                    )
                    VALUES (%s, %s, %s)
                """, (id_funcionario, hoje, agora))

                print("Entrada registrada!")

            else:

                cursor.execute("""
                    SELECT entrada, saida_intervalo, volta_intervalo, saida
                    FROM registro_ponto
                    WHERE id_funcionario = %s AND data_registro = %s
                """, (id_funcionario, hoje))

                ponto = cursor.fetchone()

                if ponto[0] and not ponto[1]:
                    cursor.execute("""
                        UPDATE registro_ponto SET saida_intervalo = %s
                        WHERE id_funcionario = %s AND data_registro = %s
                    """, (agora, id_funcionario, hoje))
                    print("Saída para intervalo registrada!")

                elif ponto[1] and not ponto[2]:
                    cursor.execute("""
                        UPDATE registro_ponto SET volta_intervalo = %s
                        WHERE id_funcionario = %s AND data_registro = %s
                    """, (agora, id_funcionario, hoje))
                    print("Volta do intervalo registrada!")

                elif ponto[2] and not ponto[3]:
                    cursor.execute("""
                        UPDATE registro_ponto SET saida = %s
                        WHERE id_funcionario = %s AND data_registro = %s
                    """, (agora, id_funcionario, hoje))
                    print("Saída final registrada!")

                else:
                    print("Todos os pontos do dia já foram registrados!")

            conn.commit()

        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()

        finally:
            conn.close()

def calcular_horas_trabalhadas(
    id_funcionario,
    data_calculo
):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    entrada,
                    saida_intervalo,
                    volta_intervalo,
                    saida
                FROM registro_ponto
                WHERE id_funcionario = %s
                AND data_registro = %s
            """

            cursor.execute(
                sql,
                (
                    id_funcionario,
                    data_calculo
                )
            )

            registro = cursor.fetchone()

            if not registro:
                print("Nenhum ponto encontrado.")
                return

            print("\n===== HORAS TRABALHADAS =====")
            print(f"Entrada: {registro[0]}")
            print(f"Saída intervalo: {registro[1]}")
            print(f"Volta intervalo: {registro[2]}")
            print(f"Saída final: {registro[3]}")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()

def ver_banco_horas(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    entrada,
                    saida
                FROM registro_ponto
                WHERE id_funcionario = %s
                AND entrada IS NOT NULL
                AND saida IS NOT NULL
            """

            cursor.execute(sql, (id_funcionario,))

            registros = cursor.fetchall()

            total_segundos = 0

            for r in registros:

                entrada = r[0]
                saida = r[1]

                dt_entrada = datetime.combine(
                    date.today(),
                    entrada
                )

                dt_saida = datetime.combine(
                    date.today(),
                    saida
                )

                diferenca = dt_saida - dt_entrada

                total_segundos += diferenca.total_seconds()

            horas = int(total_segundos // 3600)
            minutos = int((total_segundos % 3600) // 60)

            print(f"""
===================================
BANCO DE HORAS
===================================

Total horas trabalhadas:
{horas}h {minutos}min

""")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()