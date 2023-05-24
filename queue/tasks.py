import time

import requests
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery("tasks", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


GENERATOR_ENDPOINT = "http://generator-srv:5000"


@app.task()
def generate_certificates(payload):
    logger.info("Got Request - Starting work ")
    time.sleep(4)
    response = requests.post(
        f"{GENERATOR_ENDPOINT}/api/generate-certificates", json=payload
    )
    logger.info("Work Finished ")
    logger.info(response)
    return "Done"
