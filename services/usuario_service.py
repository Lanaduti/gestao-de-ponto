import bcrypt

from config.conexao import conectar_banco


def cadastrar_usuario(
    email,
    senha,
    tipo,
    id_funcionario
):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            senha_hash = bcrypt.hashpw(
                senha.encode(),
                bcrypt.gensalt()
            ).decode()

            sql = """
                INSERT INTO usuario
                (
                    email,
                    senha,
                    tipo,
                    id_funcionario
                )
                VALUES (%s, %s, %s, %s)
            """

            valores = (
                email,
                senha_hash,
                tipo,
                id_funcionario
            )

            cursor.execute(sql, valores)

            conn.commit()

            print("Usuário cadastrado!")

        except Exception as e:
            print(f"Erro: {e}")

            conn.rollback()

        finally:
            conn.close()


def login(email, senha):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    id,
                    email,
                    senha,
                    tipo,
                    id_funcionario
                FROM usuario
                WHERE email = %s
            """

            cursor.execute(sql, (email,))

            usuario = cursor.fetchone()

            if usuario:

                senha_hash = usuario[2]

                senha_correta = bcrypt.checkpw(
                    senha.encode(),
                    senha_hash.encode()
                )

                if senha_correta:

                    return {
                        "id": usuario[0],
                        "email": usuario[1],
                        "tipo": usuario[3],
                        "id_funcionario": usuario[4]
                    }

            return None

        except Exception as e:
            print(f"Erro no login: {e}")

        finally:
            conn.close()


def redefinir_senha(
    email,
    nova_senha
):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            senha_hash = bcrypt.hashpw(
                nova_senha.encode(),
                bcrypt.gensalt()
            ).decode()

            sql = """
                UPDATE usuario
                SET senha = %s
                WHERE email = %s
            """

            cursor.execute(
                sql,
                (
                    senha_hash,
                    email
                )
            )

            conn.commit()

            if cursor.rowcount > 0:

                print("""
Senha redefinida com sucesso!
""")

            else:

                print("""
E-mail não encontrado!
""")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()