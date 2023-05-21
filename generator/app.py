import base64
import io
import os
import zipfile

import pandas as pd
from flask import Flask, jsonify, make_response, render_template, request

from s3 import S3Instance
from utils import convert_html_to_pdf, get_html_content

app = Flask(__name__)
s3_obj = S3Instance()


@app.context_processor
def utility_processor():
    def get_image_file_as_base64_data(filename):
        response = s3_obj.client.get_object(Bucket=s3_obj.bucket_name, Key=filename)
        image_content = response["Body"].read()
        encoded_image = base64.b64encode(image_content).decode()
        return encoded_image

    return dict(get_image_file_as_base64_data=get_image_file_as_base64_data)


@app.route("/", methods=["GET"])
def check_health():
    return "Successful"


@app.route("/generate-certificates", methods=["POST"])
def generate_certificates():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]

    if file.filename.split(".")[-1] not in ["xls", "xlsx"]:
        return "Invalid file type", 400

    template_name = request.form.get("template_name", "template.html")
    campaign_name = request.form.get("campaign_name", "default")

    buffer = io.BytesIO(file.read())
    df = pd.read_excel(buffer)
    buffer.close()

    with open(f"templates/{template_name}", "wb") as f:
        ok = s3_obj.download_file(template_name, f)
        if not ok:
            return jsonify({"Fail to load template"}), 500

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

    zip_data = io.BytesIO()
    with zipfile.ZipFile(zip_data, mode="w") as zip_file:
        for k, pdf in pdf_data.items():
            zip_file.writestr(f"{k}_certificate.pdf", pdf)

    response = make_response(zip_data.getvalue())
    response.headers["Content-Type"] = "application/zip"
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={campaign_name}_certificates.zip"
    return response


@app.route("/upload-to-bucket", methods=["POST"])
def upload_to_bucket():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]

    upload_type = request.form.get("type")

    prefix = "templates" if upload_type == "templates" else "static"
    object_name = prefix + "/" + file.filename


    if s3_obj.upload_file(file, object_name):
        return jsonify({"message": "FIle uploaded successfully"}), 200
    else:
        return jsonify({"message": "Failed to upload file"}), 500
