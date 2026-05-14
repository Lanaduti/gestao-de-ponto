import psycopg2

def conectar_banco():
    """Tenta conectar ao banco de dados e retorna a conexão."""
    try:
        # Lembre-se de colocar sua senha real do Postgres aqui!
        conn = psycopg2.connect(
            host="localhost",         
            database="rh_sistema",    # O nome do banco que você criou
            user="postgres",          
            password="Lana8649",     # <--- COLOQUE SUA SENHA AQUI
            port="5432",     

            options='-c lc_messages=C'          
        )
        return conn
    except Exception as e:
        print(f" Erro ao conectar ao banco de dados: {e}")
        return None
