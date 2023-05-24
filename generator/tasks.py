from flask import Blueprint, jsonify, request
from s3 import S3Instance
from utils import prepare_certificates

task_route = Blueprint("task_route", __name__)


@task_route.route("/api/generate-certificates", methods=["POST"])
def generate_certificates():
    file_url = request.json["file_url"]

    template_key = request.json["template_key"]
    campaign_name = request.json["campaign_name"]

    s3_obj = S3Instance()

    with open(f"templates/{template_key}", "wb") as f:
        ok = s3_obj.download_file(f"templates/{template_key}", f)
        if not ok:
            return jsonify({"message": "Fail to load template"}), 500

    prepare_certificates(file_url, s3_obj, template_key, campaign_name)

    return jsonify({"message": "Certificate generated"}), 201
