from datetime import datetime
from app import db

class FileRecord(db.Model):
    __tablename__ = "file_records"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(10), nullable=False)
    object_key = db.Column(db.String(512), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime,  default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "file_name": self.file_name,
            "provider": self.provider,
            "object_key": self.object_key,
            "url": self.url,
            "uploaded_at": self.uploaded_at.isoformat()
        }
