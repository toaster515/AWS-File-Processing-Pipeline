from app.extensions.celery import celery
from app.extensions.db import db
from app.models.file_record import FileRecord
from datetime import datetime

@celery.task
def save_metadata_to_db(idx, file_name, folder_name, object_key, url, mime_type, description, tags):
    record = FileRecord(
        id=idx,
        file_name=file_name,
        folder_name=folder_name,
        object_key=object_key,
        url=url,
        mime_type=mime_type,
        uploaded_at=datetime.now(),
        description=description,
        tags=tags.split(",") if tags else None
    )
    db.session.add(record)
    db.session.commit()

