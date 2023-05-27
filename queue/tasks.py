import requests
from celery import Celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

app = Celery("tasks", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


@app.task()
def generate_certificates(event):
    logger.info("Got Request - Starting work ")
    response = requests.post("http://event-bus-srv:5005/events", json=event)
    logger.info("Work Finished ")
    logger.info(response)
    return "Done"
