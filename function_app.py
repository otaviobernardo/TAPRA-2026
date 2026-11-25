import base64
import datetime
import decimal
import json
import logging
import os
import uuid

import azure.functions as func
import pyodbc
from azure.storage.blob import BlobServiceClient, ContentSettings

app = func.FunctionApp()

host_sql = os.getenv("HOST")
database_sql = os.getenv("DATABASE")
user_sql = os.getenv("SQL_USER")
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

# Destino: Data Lake (Storage Account com namespace hierarquico)
DATALAKE_CONNECTION_STRING = os.getenv("DATALAKE_CONNECTION_STRING")
BRONZE_CONTAINER = os.getenv("BRONZE_CONTAINER", "bronze")
FONTE = "itsm"

# Frequencia de extracao (a cada hora, no minuto 0)
SCHEDULE = "0 0 * * * *"


def _json_default(valor):
    """Converte tipos retornados pelo pyodbc que o json nao serializa nativamente."""
    if isinstance(valor, (datetime.datetime, datetime.date, datetime.time)):
        return valor.isoformat()
    if isinstance(valor, decimal.Decimal):
        return str(valor)
    if isinstance(valor, uuid.UUID):
        return str(valor)
    if isinstance(valor, (bytes, bytearray)):
        return base64.b64encode(valor).decode("ascii")
    raise TypeError(f"Tipo nao serializavel: {type(valor)}")


def _montar_caminho(entidade: str, momento: datetime.datetime) -> str:
    """itsm/<entidade>/ano=YYYY/mes=MM/dia=DD/<entidade>_YYYYMMDDTHHMMSSZ.json"""
    return (
        f"{FONTE}/{entidade}/"
        f"ano={momento:%Y}/mes={momento:%m}/dia={momento:%d}/"
        f"{entidade}_{momento:%Y%m%dT%H%M%SZ}.json"
    )


def extract_to_bronze(tabela: str, entidade: str) -> str:
    """Le a tabela inteira do banco de origem e grava como JSON no container bronze."""
    momento = datetime.datetime.now(datetime.timezone.utc)

    try:
        conn = pyodbc.connect(conn_str_source, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {FONTE}.{tabela}")
            colunas = [col[0] for col in cursor.description]
            registros = [dict(zip(colunas, row, strict=False)) for row in cursor.fetchall()]
        finally:
            conn.close()
    except Exception as e:
        logging.error(f"[{entidade}] Erro ao extrair dados de {FONTE}.{tabela}: {e}")
        raise

    conteudo = json.dumps(registros, default=_json_default, ensure_ascii=False)
    caminho = _montar_caminho(entidade, momento)

    try:
        service = BlobServiceClient.from_connection_string(DATALAKE_CONNECTION_STRING)
        blob = service.get_blob_client(container=BRONZE_CONTAINER, blob=caminho)
        blob.upload_blob(
            conteudo.encode("utf-8"),
            overwrite=True,
            content_settings=ContentSettings(content_type="application/json"),
        )
    except Exception as e:
        logging.error(
            f"[{entidade}] Erro ao gravar no Data Lake ({BRONZE_CONTAINER}/{caminho}): {e}"
        )
        raise

    logging.info(
        f"[{entidade}] {len(registros)} registro(s) gravado(s) em {BRONZE_CONTAINER}/{caminho}"
    )
    return f"{BRONZE_CONTAINER}/{caminho}"


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_analista(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("analista", "analistas")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_categoria(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("categoria", "categorias")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_chamado(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("chamado", "chamados")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_chamado_sla(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("chamado_sla", "chamados_sla")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_chamado_status_hist(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("chamado_status_historico", "chamados_status_historico")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_cliente_organizacao(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("cliente_organizacao", "clientes_organizacao")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_csat_avaliacao(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("csat_avaliacao", "csat_avaliacoes")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_fila(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("fila", "filas")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_sla(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("sla", "slas")


@app.timer_trigger(schedule=SCHEDULE, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_solicitante(myTimer: func.TimerRequest) -> None:
    extract_to_bronze("solicitante", "solicitantes")


# Tabelas de origem e entidades de destino, usadas pela extracao manual via HTTP
TABELAS = {
    "analistas": "analista",
    "categorias": "categoria",
    "chamados": "chamado",
    "chamados_sla": "chamado_sla",
    "chamados_status_historico": "chamado_status_historico",
    "clientes_organizacao": "cliente_organizacao",
    "csat_avaliacoes": "csat_avaliacao",
    "filas": "fila",
    "slas": "sla",
    "solicitantes": "solicitante",
}


@app.route(route="extrair_agora", auth_level=func.AuthLevel.FUNCTION)
def extrair_agora(req: func.HttpRequest) -> func.HttpResponse:
    """Roda a extracao na hora. Use ?entidade=<nome> para uma so; sem parametro, roda todas."""
    entidade = req.params.get("entidade")
    if entidade and entidade not in TABELAS:
        return func.HttpResponse(
            f"Entidade desconhecida: {entidade}. Opcoes: {', '.join(TABELAS)}", status_code=400
        )

    alvos = {entidade: TABELAS[entidade]} if entidade else TABELAS
    resultados = {}
    houve_erro = False
    for nome, tabela in alvos.items():
        try:
            resultados[nome] = {"ok": True, "arquivo": extract_to_bronze(tabela, nome)}
        except Exception as e:
            houve_erro = True
            resultados[nome] = {"ok": False, "erro": str(e)}

    return func.HttpResponse(
        json.dumps(resultados, ensure_ascii=False, indent=2),
        status_code=500 if houve_erro else 200,
        mimetype="application/json",
    )


# ---------------------------------------------------------------------------
# Carga do banco de destino (bronze -> dbo), uma vez ao dia
# ---------------------------------------------------------------------------

# Credenciais do banco de destino, definidas nas variaveis de ambiente da Function App
dest_host = os.getenv("DEST_HOST")
dest_database = os.getenv("DEST_DATABASE")
dest_user = os.getenv("DEST_USER")
dest_password = os.getenv("DEST_PASSWORD")

conn_str_destino = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER=tcp:{dest_host},1433;"
    f"DATABASE={dest_database};"
    f"UID={dest_user};"
    f"PWD={dest_password};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=60;"
)

# Todo dia as 06:00 UTC (03:00 de Brasilia)
SCHEDULE_CARGA = "0 0 6 * * *"

# Ordem de carga respeitando as chaves estrangeiras: pais antes dos filhos.
# (entidade no bronze, tabela no destino)
ORDEM_CARGA = [
    ("filas", "fila"),
    ("slas", "sla"),
    ("categorias", "categoria"),
    ("clientes_organizacao", "cliente_organizacao"),
    ("analistas", "analista"),
    ("solicitantes", "solicitante"),
    ("chamados", "chamado"),
    ("chamados_sla", "chamado_sla"),
    ("chamados_status_historico", "chamado_status_historico"),
    ("csat_avaliacoes", "csat_avaliacao"),
]


def _ler_json_mais_recente(container_client, entidade: str) -> tuple[str, list]:
    """Retorna (caminho, registros) do JSON mais recente da entidade no bronze."""
    nomes = [b.name for b in container_client.list_blobs(name_starts_with=f"{FONTE}/{entidade}/")]
    if not nomes:
        raise RuntimeError(f"Nenhum arquivo encontrado em {BRONZE_CONTAINER}/{FONTE}/{entidade}/")
    # O caminho tem ano=/mes=/dia= e o timestamp no nome, entao a ordem alfabetica e cronologica
    caminho = max(nomes)
    conteudo = container_client.download_blob(caminho).readall()
    return caminho, json.loads(conteudo)


def _converter(coluna: str, valor):
    """Converte as datas ISO do JSON de volta para datetime (colunas dt_*)."""
    if isinstance(valor, str) and coluna.startswith("dt_"):
        return datetime.datetime.fromisoformat(valor)
    return valor


def carregar_destino() -> dict:
    """Recarrega todas as tabelas do destino a partir do bronze, numa unica transacao."""
    service = BlobServiceClient.from_connection_string(DATALAKE_CONNECTION_STRING)
    container = service.get_container_client(BRONZE_CONTAINER)

    dados = {}
    for entidade, tabela in ORDEM_CARGA:
        caminho, registros = _ler_json_mais_recente(container, entidade)
        logging.info(f"[carga] {tabela}: {len(registros)} registro(s) lidos de {caminho}")
        dados[tabela] = registros

    conn = pyodbc.connect(conn_str_destino, autocommit=False)
    try:
        cursor = conn.cursor()
        cursor.fast_executemany = True

        # Apaga dos filhos para os pais, para nao violar as chaves estrangeiras
        for _, tabela in reversed(ORDEM_CARGA):
            cursor.execute(f"DELETE FROM dbo.{tabela}")

        # Insere dos pais para os filhos
        resultado = {}
        for _, tabela in ORDEM_CARGA:
            registros = dados[tabela]
            if registros:
                colunas = list(registros[0].keys())
                sql = (
                    f"INSERT INTO dbo.{tabela} ({', '.join(colunas)}) "
                    f"VALUES ({', '.join('?' for _ in colunas)})"
                )
                linhas = [[_converter(c, r.get(c)) for c in colunas] for r in registros]
                cursor.executemany(sql, linhas)
            resultado[tabela] = len(registros)
            logging.info(f"[carga] {tabela}: {len(registros)} linha(s) inserida(s)")

        conn.commit()
    except Exception as e:
        conn.rollback()
        logging.error(f"[carga] Erro ao carregar o banco de destino, transacao desfeita: {e}")
        raise
    finally:
        conn.close()

    return resultado


@app.timer_trigger(
    schedule=SCHEDULE_CARGA, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def load_destino(myTimer: func.TimerRequest) -> None:
    carregar_destino()


@app.route(route="carregar_agora", auth_level=func.AuthLevel.FUNCTION)
def carregar_agora(req: func.HttpRequest) -> func.HttpResponse:
    """Roda a carga do destino na hora e devolve as linhas inseridas por tabela."""
    try:
        resultado = {"ok": True, "linhas_inseridas": carregar_destino()}
        status = 200
    except Exception as e:
        resultado = {"ok": False, "erro": str(e)}
        status = 500

    return func.HttpResponse(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        status_code=status,
        mimetype="application/json",
    )
