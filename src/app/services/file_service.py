import uuid
from app.services.storage.s3_service import S3StorageService
from app.services.storage.blob_service import BlobStorageService
from app.tasks.file_tasks import save_metadata_to_db

def handle_file_upload(file, provider):
    object_key = f"files/{uuid.uuid4()}-{file.filename}"

    if provider.upper() == 'S3':
        storage = S3StorageService()
    elif provider.upper() == 'AZURE':
        storage = BlobStorageService()
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    url = storage.upload_file(file, object_key)

    save_metadata_to_db.delay(file.filename, provider, object_key, url)

    return {"message": "Upload queued", "object_key": object_key, "url": url}
