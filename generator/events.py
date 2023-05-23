import hashlib
import logging

import pandas as pd
from celery import Celery
from flask import jsonify

from models import CertificateModel
from s3 import S3Instance

logger = logging.getLogger(__name__)
from db import Session

celery = Celery("worker", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


def prepare_certificates(request):
    file = request.files["file"]

    s3_obj = S3Instance()
    object_name = "sheets" + "/" + file.filename

    url = s3_obj.upload_file(file, object_name)

    if not url:
        return jsonify({"message": "Internal server error"}), 500

    df = pd.read_excel(url)

    campaign_name = request.form.get("campaign_name", "default")
    payload = {
        "file_url": url,
        "template_name": request.form.get("template_name", "template.html"),
        "campaign_name": campaign_name,
    }
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
        )
        session.add(certificate)
        session.commit()
    logger.info("Generating certificates")
    r = celery.send_task("tasks.generate_certificates", kwargs={"request": payload})
    logger.info(r.backend)
