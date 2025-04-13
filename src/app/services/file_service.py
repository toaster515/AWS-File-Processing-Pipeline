import uuid
from app.services.storage.s3_service import S3StorageService

def handle_file_upload(file):
    idx = uuid.uuid4()
    object_key = f"files/{idx}"
    storage = S3StorageService()
    url, bucket = storage.upload_file(file, object_key)
    return {"idx": idx, "object_key": object_key, "bucket":bucket, "url": url}

def handle_file_download(object_key):
    storage = S3StorageService()
    file_path = storage.download_file(object_key)
    return file_path