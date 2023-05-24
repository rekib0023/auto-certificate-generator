import hashlib
import io
import logging
import pdfkit
import zipfile

from datetime import datetime

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


def zip_certificates(pdf_data, s3_obj, campaign_name):
    logger.info("Preparing zip")
    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zip_file:
        for k, pdf in pdf_data.items():
            zip_file.writestr(f"{k}_certificate.pdf", pdf)

    object_name = f"{campaign_name}/certificates"
    if not s3_obj.upload_file(zip_data, object_name):
        logger.error("Failed")
