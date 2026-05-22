from config.conexao import conectar_banco


def cadastrar_funcionario(
    nome,
    cpf,
    cargo,
    setor,
    salario_base,
    vale_transporte,
    data_admissao
):

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM funcionario WHERE cpf = %s",
                (cpf,)
            )

            cpf_existente = cursor.fetchone()

            if cpf_existente:
                print("ERRO: CPF já cadastrado!")
                return False

            sql = """
                INSERT INTO funcionario
                (
                    nome,
                    cpf,
                    cargo,
                    setor,
                    salario_base,
                    vale_transporte,
                    data_admissao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            valores = (nome, cpf, cargo, setor, salario_base, vale_transporte, data_admissao)
            cursor.execute(sql,valores)
            id_gerado = cursor.fetchone()[0]
            conn.commit()
            print(f"{nome} cadastrado com sucesso!")
            return id_gerado

        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()

        finally:
            conn.close()


def listar_funcionarios():

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            sql = """
               SELECT
                   f.id,
                   f.nome,
                   f.cargo,
                   f.data_admissao,
                   u.email
               FROM funcionario f
               LEFT JOIN usuario u
               ON f.id = u.id_funcionario
            """

            cursor.execute(sql)

            funcionarios = cursor.fetchall()

            print("\n--- FUNCIONÁRIOS ---")

            for f in funcionarios:

                print(
                    f"""
ID: {f[0]}
Nome: {f[1]}
Cargo: {f[2]}
Admissão: {f[3]}
E-mail: {f[4]}
------------------------
"""
                )

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()


def editar_funcionario(
    id_funcionario,
    nome,
    cpf,
    cargo,
    setor,
    salario_base,
    vale_transporte
):

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            sql = """
                UPDATE funcionario
                SET
                    nome = %s,
                    cpf = %s,
                    cargo = %s,
                    setor = %s,
                    salario_base = %s,
                    vale_transporte = %s
                WHERE id = %s
            """

            valores = (
                nome,
                cpf,
                cargo,
                setor,
                salario_base,
                vale_transporte,
                id_funcionario
            )

            cursor.execute(sql, valores)

            conn.commit()

            print("Funcionário atualizado!")

        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()

        finally:
            conn.close()


def excluir_funcionario(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            sql = "DELETE FROM funcionario WHERE id = %s"

            cursor.execute(sql, (id_funcionario,))

            conn.commit()

            print("Funcionário excluído!")

        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()

        finally:
            conn.close()

def buscar_funcionario(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    nome,
                    cpf,
                    cargo,
                    setor,
                    salario_base,
                    vale_transporte
                FROM funcionario
                WHERE id = %s
            """

            cursor.execute(sql, (id_funcionario,))

            funcionario = cursor.fetchone()

            return funcionario

        except Exception as e:

            print(f"Erro: {e}")

        finally:

            conn.close()