import boto3
import io
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
        return {"url":f"https://{self.bucket_name}.s3.amazonaws.com/{object_key}", "bucket":self.bucket_name}
    
    def download_file(self, object_key):
        file_path = f"/tmp/{object_key.split('/')[-1]}"
        self.s3.download_file(self.bucket_name, object_key, file_path)
        return file_path
    
    def download_file_to_memory(self, object_key):
        file_obj = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)

        file = io.BytesIO(file_obj['Body'].read())

        if file.getbuffer().nbytes==0:
            return None
        else:
            file.seek(0)
            return file
