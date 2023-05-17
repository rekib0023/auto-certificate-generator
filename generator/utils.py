import hashlib
from datetime import datetime

import pdfkit


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
