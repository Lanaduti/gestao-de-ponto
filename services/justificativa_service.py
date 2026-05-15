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