import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def obter_conexao():
    conexao = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conexao

if __name__ == "__main__":
    try:
        con = obter_conexao()
        if con.is_connected():
            print("Conexão com MySQL estabelecida com sucesso!")
            con.close()
    except Exception as e:
        print(f"Falha na conexão: {e}")