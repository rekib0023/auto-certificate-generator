import logging

import boto3
from botocore.exceptions import ClientError


class S3Instance:
    def __init__(self, use_localstack=False, bucket_name="certificate-templates"):
        self.kwargs = {}
        if use_localstack:
            self.kwargs["endpoint_url"] = "http://0.0.0.0:4566"

        self.client = boto3.client("s3", **self.kwargs)
        self.bucket_name = bucket_name

    def upload_file(self, file, object_name=None):
        if object_name is None:
            object_name = file.filename

        try:
            self.client.upload_fileobj(file, self.bucket_name, object_name)
        except ClientError as e:
            logging.error(e)
            return False

        return True

    def download_file(self, filepath, file_obj):
        try:
            self.client.download_fileobj(self.bucket_name, filepath, file_obj)
            file_obj.seek(0)
            return True
        except ClientError as e:
            logging.error(e)
            return False
