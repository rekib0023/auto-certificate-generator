import os
from flask import current_app
import boto3

class S3Instance:
    def __init__(self, bucket_name="certificate-templates"):
        self.kwargs = {}
        if bool(int(os.environ.get("USE_LOCALSTACK", "0"))):
            current_app.logger.info("Using Localstack")

            self.kwargs = {
                "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
                "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                "endpoint_url": os.environ["LOCALSTACK_ENDPOINT"],
            }

        self.client = boto3.client("s3", **self.kwargs)
        self.bucket_name = bucket_name