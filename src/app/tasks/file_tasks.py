from app.extensions.celery import celery
from app.extensions.db import db
from app.models.file_record import FileRecord

@celery.task
def save_metadata_to_db(file_name, provider, object_key, url):
    record = FileRecord(
        file_name=file_name,
        provider=provider,
        object_key=object_key,
        url=url
    )
    db.session.add(record)
    db.session.commit()
