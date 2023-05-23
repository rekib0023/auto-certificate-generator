import base64
import logging

from flask import Flask, jsonify, request
from flask_migrate import Migrate

from events import prepare_certificates
from s3 import S3Instance
from tasks import task_route

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

app.register_blueprint(task_route)
logger = app.logger

from db import init_db

db = init_db(app)


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


@app.route("/events", methods=["POST"])
def events():
    data = request.form
    event_type = data["type"]

    match event_type:
        case "CAMPAIGN_CREATED":
            prepare_certificates(request)
        case "CERTIFICATE_GENERATED":
            pass
