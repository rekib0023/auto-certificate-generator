import base64
import logging

from db import SQLALCHEMY_URI
from dotenv import load_dotenv
from events import prepare_certificates
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from models import CertificateModel, db
from s3 import S3Instance
from tasks import task_route

load_dotenv(".env")

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

app.register_blueprint(task_route)
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
    data = request.json
    logger.info(data)
    event_type = data.pop("type")

    match event_type:
        case "CAMPAIGN_CREATED":
            prepare_certificates(data)
        case "CERTIFICATE_GENERATED":
            pass
    return {"status": "OK"}