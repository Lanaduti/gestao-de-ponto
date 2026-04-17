from funcionario import Funcionario
from conexao import conectar_banco

class SistemaRH:
    def __init__(self):
        pass

    def cadastrar_funcionario(self, nome, cpf, cargo, setor, salario_base, data_admissao):
        conn = conectar_banco()
        
        if conn:
            try:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO funcionario (nome, cpf, cargo, setor, salario_base, data_admissao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (nome, cpf, cargo, setor, salario_base, data_admissao)
                cursor.execute(sql, valores)
                conn.commit()
                print(f" Funcionário(a) '{nome}' cadastrado(a) com sucesso no Banco de Dados!")
                cursor.close()
                return True
                
            except Exception as e:
                print(f" Erro ao cadastrar no banco: {e}")
                conn.rollback() 
                return False
            finally:
                conn.close()
        else:
            print("Não foi possível conectar ao banco para realizar o cadastro.")
            return False

    def listar_funcionarios(self):
        conn = conectar_banco()
        
        if conn:
            try:
                cursor = conn.cursor()
                sql = "SELECT id, nome, cpf, cargo, setor, salario_base, data_admissao FROM funcionario"
                cursor.execute(sql)
                
                resultados = cursor.fetchall()

                print("\n---  Lista de Funcionários (Direto do Banco de Dados) ---")
                
                if not resultados:
                    print("Nenhum funcionário cadastrado no momento.")
                else:
                    for linha in resultados:
                        print(f"ID: {linha[0]:02d} | Nome: {linha[1]:<15} | Cargo: {linha[3]:<20} | Admissão: {linha[6]}")
                
                print("-" * 65)
                
                cursor.close()
            except Exception as e:
                print(f" Erro ao buscar dados no banco: {e}")
            finally:
                conn.close()
        else:
            print("Sem conexão com o banco de dados.")