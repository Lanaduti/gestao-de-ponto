from conexao import conectar_banco


def visualizar_perfil(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    f.nome,
                    f.cpf,
                    f.cargo,
                    f.setor,
                    f.salario_base,
                    f.data_admissao,
                    u.email
                FROM funcionario f
                LEFT JOIN usuario u
                ON f.id = u.id_funcionario
                WHERE f.id = %s
            """

            cursor.execute(
                sql,
                (id_funcionario,)
            )

            funcionario = cursor.fetchone()

            if funcionario:

                print(f"""
===================================
MEU PERFIL
===================================

Nome: {funcionario[0]}
CPF: {funcionario[1]}
Cargo: {funcionario[2]}
Setor: {funcionario[3]}
Salário: R$ {funcionario[4]}
Admissão: {funcionario[5]}
E-mail: {funcionario[6]}

""")

            else:

                print("Funcionário não encontrado.")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()