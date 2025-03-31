import boto3
from flask import current_app
from app.services.storage.storage_interface import StorageInterface

class S3StorageService(StorageInterface):
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"]
        )
        self.bucket_name = current_app.config["AWS_S3_BUCKET_NAME"]

    def upload_file(self, file_obj, object_key):
        self.s3.upload_fileobj(file_obj, self.bucket_name, object_key)
        return f"https://{self.bucket_name}.s3.amazonaws.com/{object_key}"
