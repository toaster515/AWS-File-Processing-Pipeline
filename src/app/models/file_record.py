from datetime import datetime
from app import db

class FileRecord(db.Model):
    __tablename__ = "file_records"

    id = db.Column(db.Guid, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    folder_name = db.Column(db.String(255), nullable=True)
    object_key = db.Column(db.String(512), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime,  default=datetime.now)
    mime_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512), nullable=True)
    tags = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "object_key": self.object_key,
            "url": self.url,
            "uploaded_at": self.uploaded_at.isoformat(),
            "mime_type": self.mime_type,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else []
        }
