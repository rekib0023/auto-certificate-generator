import logging
import os

import boto3
from botocore.exceptions import ClientError


class S3Instance:
    def __init__(self, bucket_name="certificate-templates"):
        self.kwargs = {}
        if bool(int(os.environ.get("USE_LOCALSTACK", "0"))):
            self.kwargs["endpoint_url"] = os.environ["LOCALSTACK_ENDPOINT"]

        self.client = boto3.client("s3", **self.kwargs)
        self.bucket_name = bucket_name

        self.create_bucket()

    def create_bucket(self):
        # Check if the bucket exists
        response = self.client.list_buckets()

        for bucket in response['Buckets']:
            if bucket['Name'] == self.bucket_name:
                print(f"Bucket '{self.bucket_name}' already exists.")
                break
        else:
            # Create the bucket
            self.client.create_bucket(Bucket=self.bucket_name)
            print(f"Bucket '{self.bucket_name}' created successfully.")
        

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
