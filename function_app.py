import azure.functions as func
import os
import logging 
import pyodbc

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado(myTimer:func.TimerRequest) -> None:
    host_sql =  os.getenv("HOST")
    database_sql = os.getenv("DATABASE")
    user_sql = os.getenv("USER")
    password_sql = os.getenv("PASSWORD")

    conn_str_source = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={host_sql};"
        f"DATABASE={database_sql};"
        f"UID={user_sql};"
        f"PWD={password_sql};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Chamado encontrado: {row[0]}")
        else:
            logging.info("Nenhum chamado encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")
if __name__ == "__main__":
    extract_chamado(func.TimerRequest)