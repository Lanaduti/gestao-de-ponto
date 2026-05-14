from conexao import conectar_banco


def gerar_contracheque(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    nome,
                    cargo,
                    salario_base
                FROM funcionario
                WHERE id = %s
            """

            cursor.execute(sql, (id_funcionario,))

            funcionario = cursor.fetchone()

            if funcionario:

                print("\n===== CONTRACHEQUE =====")

                print(f"Nome: {funcionario[0]}")
                print(f"Cargo: {funcionario[1]}")
                print(f"Salário: R$ {funcionario[2]}")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()