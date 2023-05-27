import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Instance:
    def __init__(self, bucket_name="certificate-templates"):
        self.kwargs = {}
        if bool(int(os.environ.get("USE_LOCALSTACK", "0"))):
            logger.info("Using Localstack")

            self.kwargs = {
                "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
                "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
                "endpoint_url": os.environ['LOCALSTACK_ENDPOINT'],
            }

        self.client = boto3.client("s3", **self.kwargs)
        self.bucket_name = bucket_name

    def upload_file(self, file, object_name=None):
        if object_name is None:
            object_name = file.filename

        try:
            self.client.upload_fileobj(file, self.bucket_name, object_name)
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=3600,
            )
            logger.info("Uploaded successfully")
            return url
        except ClientError as e:
            logger.error(e)
            return None

    def download_file(self, filepath, file_obj):
        try:
            self.client.download_fileobj(self.bucket_name, filepath, file_obj)
            file_obj.seek(0)
            return True
        except ClientError as e:
            logger.error(e)
            return False
