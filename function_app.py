import azure.functions as func
import os
import logging 
import pyodbc

app = func.FunctionApp()

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

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_analista(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.analista")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Analista encontrado: {row[0]}")
        else:
            logging.info("Nenhum analista encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_categoria(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.categoria")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Categoria encontrada: {row[0]}")
        else:
            logging.info("Nenhuma categoria encontrada.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.chamado")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Chamado encontrado: {row[0]}")
        else:
            logging.info("Nenhum chamado encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado_sla(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.chamado_sla")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"SLA de chamado encontrado: {row[0]}")
        else:
            logging.info("Nenhum SLA de chamado encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado_status_hist(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.chamado_status_historico")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Status do chamado encontrado: {row[0]}")
        else:
            logging.info("Nenhum status do chamado encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_cliente_organizacao(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.cliente_organizacao")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Organização do cliente encontrada: {row[0]}")
        else:
            logging.info("Nenhuma organização do cliente encontrada.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_csat_avaliacao(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.csat_avaliacao")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Avaliação CSAT encontrada: {row[0]}")
        else:
            logging.info("Nenhuma avaliação CSAT encontrada.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_fila(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.fila")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Fila encontrada: {row[0]}")
        else:
            logging.info("Nenhuma fila encontrada.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_sla(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.sla")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"SLA encontrado: {row[0]}")
        else:
            logging.info("Nenhum SLA encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_solicitante(myTimer:func.TimerRequest) -> None:
    try:
        conn = pyodbc.connect(
            conn_str_source,
            timeout=30
        )

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM itsm.solicitante")

        row = cursor.fetchone()
        
        if row:
            logging.info(f"Solicitante encontrado: {row[0]}")
        else:
            logging.info("Nenhum solicitante encontrado.")
            
            
    except Exception as e:
        logging.error(f"Erro ao conectar ou executar no banco de dados: {e}")

if __name__ == "__main__":
    extract_chamado(func.TimerRequest)