import uuid
from app.tasks.record_tasks import save_metadata_to_db
from app.models.file_record import FileRecord

def handle_metadata_upload(metadata):
    """
    Process metadata and save it to the database.
    """
    # Extract metadata fields
    idx = metadata.get("id", uuid.uuid4())
    file_name = metadata.get("file_name")
    folder_name = metadata.get("folder_name", "files")
    object_key = metadata.get("object_key")
    url = metadata.get("url")
    mime_type = metadata.get("mime_type")
    description = metadata.get("description", "")
    tags = ",".join(metadata.get("tags", []))

    # Save metadata to the database asynchronously
    save_metadata_to_db.delay(idx, file_name, folder_name, object_key, url, mime_type, description, tags)

    return {"message": "Metadata storage queued", "idx": idx}

def get_record_by_id(record_id):
    """
    Get file record metadata by id.
    """
    # Get metadata from the database
    record = FileRecord.query.get(record_id)
    return record.to_dict() if record else None