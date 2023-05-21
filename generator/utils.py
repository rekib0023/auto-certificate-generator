import hashlib
import io
import os
import zipfile
from datetime import datetime

import pandas as pd
import pdfkit
from flask import render_template

import logging

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


def get_html_content(data):
    now = datetime.now()
    html_context = {
        "name": data.first_name + " " + data.last_name,
        "email": data.email,
        "start_date": data.start_date.strftime("%B %d, %Y"),
        "end_date": data.end_date.strftime("%B %d, %Y"),
        "certification_date": now.strftime("%B %dth %Y"),
    }
    html_context["certification_number"] = (
        hashlib.shake_256(html_context["name"].encode()).hexdigest(4)
        + "-"
        + str(int(now.timestamp()))
    )

    return html_context


def prepare_certificate_zip(file_name, s3_obj, template_name, campaign_name):
    logger.info("Preparing certificates")
    df = pd.read_excel(f"sheets/{file_name}")

    pdf_data = {}
    for row in df.itertuples():
        html_content = get_html_content(row)
        html = render_template(template_name, **html_content)
        pdf = convert_html_to_pdf(html)
        pdf_data[row.first_name + "_" + row.last_name] = pdf
        object_name = f'certificates/{campaign_name}/{row.first_name + "_" + row.last_name}_certificate.pdf'
        in_memory_file = io.BytesIO(pdf)
        s3_obj.upload_file(in_memory_file, object_name)
        in_memory_file.close()

    os.remove(f"templates/{template_name}")
    os.remove(f"sheets/{file_name}")

    logger.info("Preparing zip")
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zip_file:
        for k, pdf in pdf_data.items():
            zip_file.writestr(f"{k}_certificate.pdf", pdf)

    object_name = f"{campaign_name}/certificates"
    if not s3_obj.upload_file(zip_data, object_name):
        logger.error("Failed")