import base64

from celery import Celery
from flask import Flask, jsonify, request
from s3 import S3Instance
from tasks import task_route
import logging

app = Flask(__name__)

app.logger.setLevel(logging.DEBUG)

app.register_blueprint(task_route)
logger = app.logger

celery = Celery("worker", broker="amqp://admin:mypass@rabbit:5672", backend="rpc://")


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


@app.route("/create-campaign", methods=["POST"])
def create_campaign():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]

    if file.filename.split(".")[-1] not in ["xls", "xlsx"]:
        return "Invalid file type", 400

    s3_obj = S3Instance()
    object_name = "sheets" + "/" + file.filename

    if not s3_obj.upload_file(file, object_name):
        return jsonify({"message": "Internal server error"}), 500

    form_data = {
        "file_name": file.filename,
        "template_name": request.form.get("template_name", "template.html"),
        "campaign_name": request.form.get("campaign_name", "default"),
    }

    logger.info("Generating certificates")
    r = celery.send_task("tasks.generate_certificates", kwargs={"request": form_data})
    logger.info(r.backend)
    return jsonify(
        {
            "message": "Campaign created successfully",
            "task_id": r.id,
        },
        201,
    )


@app.route("/upload-to-bucket", methods=["POST"])
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


@app.route('/task_status/<task_id>')
def get_status(task_id):
    status = celery.AsyncResult(task_id, app=celery)
    print("Invoking Method ")
    return "Status of the Task " + str(status.state)


@app.route('/task_result/<task_id>')
def task_result(task_id):
    result = celery.AsyncResult(task_id).result
    return "Result of the Task " + str(result)