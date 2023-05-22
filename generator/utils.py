import hashlib
import io
import logging
import os
import zipfile
from datetime import datetime

import pandas as pd
import pdfkit
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import CertificateModel

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_DATABASE = os.environ["MYSQL_DATABASE"]
DB_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]
DB_USER = os.environ["MYSQL_USER"]


SQLALCHEMY_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8"

engine = create_engine(SQLALCHEMY_URI)

Session = sessionmaker(bind=engine)


logger = logging.getLogger(__name__)


def convert_html_to_pdf(html):
    options = {
        "page-size": "Letter",
        "margin-top": "0mm",
        "margin-right": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "dpi": "96",
        "viewport-size": "395.5x642.25",
        "orientation": "Landscape",
    }

    return pdfkit.from_string(html, False, options=options)


def get_html_content(data, campaign_name):
    now = datetime.now()
    html_context = {
        "name": data.first_name + " " + data.last_name,
        "email": data.email,
        "start_date": data.start_date.strftime("%B %d, %Y"),
        "end_date": data.end_date.strftime("%B %d, %Y"),
        "certification_date": now.strftime("%B %dth %Y"),
    }
    html_context["certificate_number"] = (
        hashlib.shake_256(html_context["name"].encode()).hexdigest(4)
        + "_"
        + hashlib.shake_256(campaign_name.encode()).hexdigest(4)
    )

    return html_context


def prepare_certificates(file_url, s3_obj, template_name, campaign_name):
    logger.info("Preparing certificates")
    df = pd.read_excel(file_url)

    pdf_data = {}
    for row in df.itertuples():
        html_content = get_html_content(row, campaign_name)
        html = render_template(template_name, **html_content)
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

        in_memory_file.close()

    os.remove(f"templates/{template_name}")


def zip_certificates(pdf_data, s3_obj, campaign_name):
    logger.info("Preparing zip")
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zip_file:
        for k, pdf in pdf_data.items():
            zip_file.writestr(f"{k}_certificate.pdf", pdf)

    object_name = f"{campaign_name}/certificates"
    if not s3_obj.upload_file(zip_data, object_name):
        logger.error("Failed")
