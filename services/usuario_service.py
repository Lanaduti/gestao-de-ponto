from conexao import conectar_banco


def login(email, senha):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    id,
                    email,
                    tipo,
                    id_funcionario
                FROM usuario
                WHERE email = %s
                AND senha = %s
            """

            cursor.execute(sql, (email, senha))

            usuario = cursor.fetchone()

            if usuario:

                return {
                    "id": usuario[0],
                    "email": usuario[1],
                    "tipo": usuario[2],
                    "id_funcionario": usuario[3]
                }

            else:
                return None

        except Exception as e:
            print(f"Erro no login: {e}")

        finally:
            conn.close()