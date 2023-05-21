from flask import Blueprint, current_app
from flask import jsonify, request
from s3 import S3Instance
from utils import prepare_certificate_zip

task_route = Blueprint('task_route', __name__)

@task_route.route("/generate-certificates", methods=["POST"])
def generate_certificates():
    file_name = request.json["file_name"]

    template_name = request.json["template_name"]
    campaign_name = request.json["campaign_name"]

    s3_obj = S3Instance()

    with open(f"sheets/{file_name}", "wb") as f:
        ok = s3_obj.download_file(f"sheets/{file_name}", f)
        if not ok:
            return jsonify({"message": "Fail to dowload sheet"}), 500

    with open(f"templates/{template_name}", "wb") as f:
        ok = s3_obj.download_file(f"templates/{template_name}", f)
        if not ok:
            return jsonify({"message":"Fail to load template"}), 500

    prepare_certificate_zip(file_name, s3_obj, template_name, campaign_name)

    return jsonify({"message": "Certificate generated"}), 201
