import logging
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    logging.info('TimerTriggerLog: executada com sucesso. Este e o log de exemplo do timer trigger.')
