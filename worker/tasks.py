import time

import requests
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery("tasks", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


GENERATOR_ENDPOINT = "http://generator_app:5000"


@app.task()
def generate_certificates(request):
    logger.info("Got Request - Starting work ")
    time.sleep(4)
    payload = {
        "file_url": request["file_url"],
        "template_name": request["template_name"],
        "campaign_name": request["campaign_name"],
    }
    response = requests.post(
        f"{GENERATOR_ENDPOINT}/api/generate-certificates", json=payload
    )
    logger.info("Work Finished ")
    logger.info(response)
    return "Done"
