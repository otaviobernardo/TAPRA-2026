import logging
import os
import requests
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    logging.info('TimerTriggerCaller: iniciando chamada para HttpTriggerEcho.')

    function_url = os.environ.get(
        "HTTP_FUNCTION_URL",
        "http://localhost:7071/api/HttpTriggerEcho"
    )
    parametro_enviado = "ola-vindo-do-timer-trigger"

    try:
        response = requests.get(function_url, params={"parametro": parametro_enviado}, timeout=10)
        response.raise_for_status()

        resultado = f"{response.text} [recebido e re-impresso por TimerTriggerCaller]"
        logging.info(resultado)

    except requests.exceptions.RequestException as erro:
        logging.error(f'TimerTriggerCaller: falha ao chamar HttpTriggerEcho -> {erro}')
