import base64
import hashlib
import logging
import os

import pandas as pd
from celery import Celery
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from models import CertificateModel
from s3 import S3Instance
from tasks import task_route

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

app.register_blueprint(task_route)
logger = app.logger


celery = Celery("worker", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_DATABASE = os.environ["MYSQL_DATABASE"]
DB_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]
DB_USER = os.environ["MYSQL_USER"]


SQLALCHEMY_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8"
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_URI
db = SQLAlchemy(app)


with app.app_context():
    db.create_all()

migrate = Migrate(app, db)


@app.context_processor
def utility_processor():
    def get_image_file_as_base64_data(filename):
        s3_obj = S3Instance()
        response = s3_obj.client.get_object(Bucket=s3_obj.bucket_name, Key=filename)
        image_content = response["Body"].read()
        encoded_image = base64.b64encode(image_content).decode()
        return encoded_image

    return dict(get_image_file_as_base64_data=get_image_file_as_base64_data)


@app.route("/", methods=["GET"])
def check_health():
    return "Successful"


@app.route("/api/create-campaign", methods=["POST"])
def create_campaign():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]

    if file.filename.split(".")[-1] not in ["xls", "xlsx"]:
        return "Invalid file type", 400

    s3_obj = S3Instance()
    object_name = "sheets" + "/" + file.filename

    url = s3_obj.upload_file(file, object_name)

    if not url:
        return jsonify({"message": "Internal server error"}), 500

    df = pd.read_excel(url)

    campaign_name = request.form.get("campaign_name", "default")
    form_data = {
        "file_url": url,
        "template_name": request.form.get("template_name", "template.html"),
        "campaign_name": campaign_name,
    }

    logger.info("Generating certificates")

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
        db.session.add(certificate)
        db.session.commit()

    r = celery.send_task("tasks.generate_certificates", kwargs={"request": form_data})
    logger.info(r.backend)
    return jsonify(
        {
            "message": "Campaign created successfully",
            "task_id": r.id,
        },
        201,
    )


@app.route("/api/upload-to-bucket", methods=["POST"])
def upload_to_bucket():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]

    upload_type = request.form.get("type")

    prefix = "templates" if upload_type == "templates" else "static"
    object_name = prefix + "/" + file.filename

    s3_obj = S3Instance()

    if s3_obj.upload_file(file, object_name):
        return jsonify({"message": "FIle uploaded successfully"}), 200
    else:
        return jsonify({"message": "Failed to upload file"}), 500
