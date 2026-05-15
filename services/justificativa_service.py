from config.conexao import conectar_banco


def listar_justificativas():

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    id,
                    motivo,
                    status
                FROM registro_justificativa
            """

            cursor.execute(sql)

            justificativas = cursor.fetchall()

            for j in justificativas:

                print(j)

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()

def enviar_justificativa(
    id_funcionario,
    data_falta,
    motivo,
    compensacao
):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                INSERT INTO registro_justificativa
                (
                    id_funcionario,
                    data_falta,
                    motivo,
                    compensacao
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                sql,
                (
                    id_funcionario,
                    data_falta,
                    motivo,
                    compensacao
                )
            )

            conn.commit()

            print("Justificativa enviada!")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()

def atualizar_status_justificativa(
    id_justificativa,
    status
):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                UPDATE registro_justificativa
                SET status = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (
                    status,
                    id_justificativa
                )
            )

            conn.commit()

            print("Status atualizado!")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()

def ver_status_justificativa(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            sql = """
                SELECT
                    id,
                    data_falta,
                    motivo,
                    status,
                    compensacao
                FROM registro_justificativa
                WHERE id_funcionario = %s
                ORDER BY data_falta DESC
            """

            cursor.execute(sql, (id_funcionario,))
            justificativas = cursor.fetchall()

            if not justificativas:
                print("\n⚠️  Nenhuma justificativa encontrada.")
                return

            print("\n===== MINHAS JUSTIFICATIVAS =====")
            for j in justificativas:
                print(f"""
ID: {j[0]}
Data da Falta: {j[1]}
Motivo: {j[2]}
Status: {j[3]}
Compensação: {j[4]}
---------------------------------""")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()