import hashlib
import io
import json
import logging
import os
import requests

import pandas as pd
from celery import Celery
from flask import render_template, current_app

from db import Session
from models import CertificateModel
from s3 import S3Instance
from utils import convert_html_to_pdf, get_html_content


celery = Celery("worker", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


def generate_certificates(payload):
    url = payload["file_url"]
    df = pd.read_excel(url)

    campaign_name = payload["campaign_name"]
    company_name = payload["company_name"]
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
                + hashlib.shake_256(company_name.encode()).hexdigest(4)
            ),
            campaign_id=payload["campaign_id"],
        )
        session.add(certificate)
        session.commit()
    current_app.logger.info("Generating certificates")
    event = {
        "type": "PREPARE_CERTIFICATES",
        "data": payload
    }
    r = celery.send_task("tasks.generate_certificates", kwargs={"event": event})
    current_app.logger.info(r.backend)


def prepare_certificates(payload):
    file_url = payload["file_url"]

    template_key = payload["template_key"]
    campaign_name = payload["campaign_name"]
    company_name = payload["company_name"]
    company_email = payload["company_email"]

    s3_obj = S3Instance()

    with open(f"templates/{template_key}", "wb") as f:
        s3_obj.download_file(f"templates/{template_key}", f)

    current_app.logger.info("Preparing certificates")
    df = pd.read_excel(file_url)

    pdf_data = {}
    for row in df.itertuples():
        html_content = get_html_content(row, campaign_name, company_name)
        html = render_template(template_key, **html_content)
        pdf = convert_html_to_pdf(html)
        in_memory_file = io.BytesIO(pdf)
        object_name = f'certificates/{company_name}/{campaign_name}/{row.first_name + "_" + row.last_name}_certificate.pdf'
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

        if status == "Success":
            payload = json.dumps({
                        "sender": f"{company_email}",
                        "recipients": [
                            f"{html_content['email']}"
                        ],
                        "subject": "Subject",
                        "body": "Tests",
                        "attachments": [
                            {
                            "key": object_name,
                            "mime_type": "application",
                            "subtype": "pdf",
                            "filename": f'{row.first_name + "_" + row.last_name}_certificate.pdf'
                            }
                        ]
                    })
            
            response = requests.request("POST", "http://mailer-srv:5003/send", headers={
                'Content-Type': 'application/json',
            }, data=payload)
            if response.status_code == 200 and certificate:
                mail_sent = True
                current_app.logger.info("Sent mail")
            else:
                mail_sent = False
                current_app.logger.error("Failed to send mail: ")
                current_app.logger.error(response)

        if certificate:
            certificate.status = status
            certificate.s3_path = s3_path
            certificate.mail_sent = mail_sent
            session.commit()
            # send emails

        in_memory_file.close()

    os.remove(f"templates/{template_key}")
