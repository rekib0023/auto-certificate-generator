import hashlib
import logging

import pandas as pd
from celery import Celery
from models import CertificateModel

logger = logging.getLogger(__name__)
from db import Session

celery = Celery("worker", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


def prepare_certificates(data):
    url = data["file_url"]
    df = pd.read_excel(url)

    campaign_name = data["campaign_name"]
    session = Session()
    for row in df.itertuples():
        certificate = CertificateModel(
            name=f"{row.first_name}_{row.last_name}_certificate.pdf",
            certificate_number=(
                hashlib.shake_256(
                    (row.first_name + " " + row.last_name).encode()
                ).hexdigest(4)
                + "_"
                + hashlib.shake_256(campaign_name.encode()).hexdigest(4)
            ),
            campaign_id=data["campaign_id"],
        )
        session.add(certificate)
        session.commit()
    logger.info("Generating certificates")
    r = celery.send_task("tasks.generate_certificates", kwargs={"payload": data})
    logger.info(r.backend)
