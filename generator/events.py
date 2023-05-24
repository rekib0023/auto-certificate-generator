import hashlib
import io
import logging
import os

import pandas as pd
from celery import Celery
from flask import render_template

from db import Session
from models import CertificateModel
from s3 import S3Instance
from utils import convert_html_to_pdf, get_html_content

logger = logging.getLogger(__name__)

celery = Celery("worker", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


def generate_certificates(payload):
    url = payload["file_url"]
    df = pd.read_excel(url)

    campaign_name = payload["campaign_name"]
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
            campaign_id=payload["campaign_id"],
        )
        session.add(certificate)
        session.commit()
    logger.info("Generating certificates")
    event = {
        "type": "PREPARE_CERTIFICATES",
        "data": payload
    }
    r = celery.send_task("tasks.generate_certificates", kwargs={"event": event})
    logger.info(r.backend)


def prepare_certificates(payload):
    file_url = payload["file_url"]

    template_key = payload["template_key"]
    campaign_name = payload["campaign_name"]

    s3_obj = S3Instance()

    with open(f"templates/{template_key}", "wb") as f:
        s3_obj.download_file(f"templates/{template_key}", f)

    logger.info("Preparing certificates")
    df = pd.read_excel(file_url)

    pdf_data = {}
    for row in df.itertuples():
        html_content = get_html_content(row, campaign_name)
        html = render_template(template_key, **html_content)
        pdf = convert_html_to_pdf(html)
        in_memory_file = io.BytesIO(pdf)
        object_name = f'certificates/{campaign_name}/{row.first_name + "_" + row.last_name}_certificate.pdf'
        if s3_obj.upload_file(in_memory_file, object_name):
            pdf_data[row.first_name + "_" + row.last_name] = pdf
            status = "Success"
            s3_path = object_name
        else:
            status = "Failed"
            s3_path = ""
        session = Session()
        certificate = (
            session.query(CertificateModel)
            .filter_by(certificate_number=html_content["certificate_number"])
            .first()
        )

        if certificate:
            certificate.status = status
            certificate.s3_path = s3_path
            session.commit()
            # send emails

        in_memory_file.close()

    os.remove(f"templates/{template_key}")
