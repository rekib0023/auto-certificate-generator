import base64
import logging

from dotenv import load_dotenv
from flask import Flask, request
from flask_migrate import Migrate

from db import SQLALCHEMY_URI
from events import generate_certificates, prepare_certificates
from models import CertificateModel, db
from s3 import S3Instance

load_dotenv(".env")

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

logger = app.logger

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_URI
db.init_app(app)
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


@app.route("/events", methods=["POST"])
def events():
    content = request.get_json()
    event_type = content["type"]
    logger.info("Received event: ", event_type)
    data = content["data"]

    match event_type:
        case "CAMPAIGN_CREATED":
            generate_certificates(data)
        case "PREPARE_CERTIFICATES":
            prepare_certificates(data)
    return {"status": "OK"}
