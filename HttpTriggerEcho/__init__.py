import logging
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP Trigger.
    Recebe um parametro através de uma query string (get) e retorna esse valor.
    """
    logging.info('HttpTriggerEcho: requisição recebida.')

    parametro = req.params.get('parametro')

    if not parametro:
        mensagem = "Nenhum parametro recebido. Use ?parametro=valor na URL."
        logging.warning(mensagem)
        return func.HttpResponse(mensagem, status_code=400)

    logging.info(f'Parametro recebido: {parametro}')

    resposta = f"Parametro recebido: {parametro} [processado por HttpTriggerEcho]"
    return func.HttpResponse(resposta, status_code=200)
