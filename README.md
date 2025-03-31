# File Storage API Template (Flask)

A containerized Flask API template for uploading files to multiple cloud storage providers (AWS S3, Azure Blob), while recording metadata in Postgres. Supports background processing via Celery + Redis and auto-generates Swagger UI docs.

---
## Features

- Clean, modular Flask architecture
- Upload to AWS S3 or Azure Blob via pluggable storage interface
- Background task handling with Celery + Redis
- Postgres for metadata persistence
- API documentation via Swagger UI (`flasgger`)
- Auto database migrations on container startup
- Fully Dockerized for local development

---
## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-org/file-storage-api-python.git
cd file-storage-api-python/docker
```
### 2. Start the containers

```bash
docker-compose up --build
```

Once it’s up, visit:
- Swagger UI: http://localhost:8000/apidocs/
- API Endpoint: `POST /api/files/` — Upload files

---
## Example Request (via Swagger)

- `POST /api/files/`
- `Content-Type: multipart/form-data`
- `form-data` fields:
    - `file`: file to upload
    - `provider`: `"S3"` or `"AZURE"`

---
## Config

All environment variables are loaded from `.env`. See `.env.example` for local setup:

```env
SECRET_KEY=dev-secret DATABASE_URL=postgresql://postgres:postgres@postgres:5432/recordsdb CELERY_BROKER_URL=redis://redis:6379/0 CELERY_RESULT_BACKEND=redis://redis:6379/0  AWS_ACCESS_KEY_ID=your-key AWS_SECRET_ACCESS_KEY=your-secret AWS_S3_BUCKET_NAME=your-bucket  AZURE_STORAGE_CONNECTION_STRING=your-azure-conn AZURE_STORAGE_CONTAINER=your-container
```
---
## Architecture

```bash
src/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── config.py              # App settings
│   ├── routes/                # Flask Blueprints
│   ├── models/                # SQLAlchemy models
│   ├── services/              # File and storage services
│   │   └── storage/           # S3 and Azure implementations
│   ├── tasks/                 # Celery background tasks
│   └── extensions/            # DB and Celery initialization
├── run.py                     # Entry point
├── requirements.txt
└── Dockerfile
```

- Follows service-layer architecture with dependency injection via interfaces
- Easily extendable with new storage providers or background jobs

---
## Celery Worker

To start the background task worker:

```bash
docker-compose up worker
```

This listens for upload metadata tasks and writes to the Postgres DB in the background.

---
## Notes

- Flask app is served via **Gunicorn** in production mode
- DB migration is handled automatically on container boot using `flask db upgrade`
- Swagger UI powered by `flasgger` — no extra config needed

---
## Roadmap Ideas

- Add JWT auth with Flask-JWT-Extended
- Input validation with Pydantic or Marshmallow
- Pre-upload file scanning or processing pipeline
- Frontend dropzone integration (React, etc.)