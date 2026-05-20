import psycopg2

def conectar_banco():
    """Tenta conectar ao banco de dados e retorna a conexão."""
    try:
        # Configurações para PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="rh_sistemas",
            user="postgres",           # Usuário padrão do Postgres
            password="jay123", # Coloque sua senha do Postgres
            port="5432"                # Porta padrão do Postgres
        )
        return conn
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO POSTGRESQL: {e}")
        return None
