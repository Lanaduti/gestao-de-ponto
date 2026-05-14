from conexao import conectar_banco


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