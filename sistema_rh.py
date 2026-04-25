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
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id 
                """
                valores = (nome, cpf, cargo, setor, salario_base, data_admissao)
                cursor.execute(sql, valores)
                id_gerado = cursor.fetchone()[0]
                conn.commit()
                print(f" Funcionário(a) '{nome}' cadastrado(a) com sucesso no Banco de Dados!")
                cursor.close()
                return id_gerado 
                
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

    # 22/04/2026 Victor adicionando FR02 (Função criar usuário e função de login)
    def cadastrar_usuario (self, email, senha, tipo, id_funcionario):  
        conn = conectar_banco()
        if conn: 
            try: 
                cursor = conn.cursor()
                sql = """
                    INSERT INTO usuario (email, senha, tipo, id_funcionario)
                    VALUES (%s, %s, %s, %s)
                    """
                cursor.execute(sql, (email, senha, tipo, id_funcionario))
                conn.commit()
                print(f"Usuário de acesso '{email}' criado com sucesso!")
                cursor.close()
                return True 
            except Exception as e:
                print(f"Erro ao criar usuário de acesso: {e}")
                conn.rollback() 
                return False
            finally: 
                conn.close() 

    def login(self, email, senha): 
        conn = conectar_banco()
        if conn: 
            try: 
                cursor = conn.cursor()
                sql = "SELECT id, email, tipo, id_funcionario FROM usuario WHERE email = %s AND senha = %s"
                cursor.execute(sql, (email, senha))

                usuario = cursor.fetchone() 

                print("\n --- Tentativa de login ---")
                if usuario: 
                    print(f"ACESSO LIBERADO! Bem-vindo(a), {usuario[1]} (Perfil: {usuario[2]}).")
                    return True 
                else: 
                    print("ACESSO NEGADO! Email ou senha incorretos.")
                    return False    
            except Exception as e: 
                print(f"Erro no sistema de login: {e}")
                return False
            finally: 
                conn.close()













        #aqui é onde vão ficar as funções relacionados a manipulações de dados tipo cadastro e essas paradas fechouuuuuu??