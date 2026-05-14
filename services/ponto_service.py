from conexao import conectar_banco
from datetime import datetime, date


def registrar_ponto(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            agora = datetime.now().time()

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

            conn.commit()

        except Exception as e:
            print(f"Erro: {e}")
            conn.rollback()

        finally:
            conn.close()