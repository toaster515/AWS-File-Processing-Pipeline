import os
from flask import Flask
from app.extensions.db import db
from app.extensions.celery import celery
from app.routes.file_routes import file_bp
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from .config import Config
from flasgger import Swagger
from app.utils.aws_config_loader import load_secrets_from_aws

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if os.getenv("USE_AWS_SECRETS", "false").lower() == "true":
        secret_name = os.getenv("AWS_SECRET_NAME", "lambda/file-processing-creds")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        secrets = load_secrets_from_aws(secret_name, region=aws_region)
        app.config.update(secrets)

    db.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)
    
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "File Upload API",
            "description": "Multi-provider file upload API for AWS",
            "version": "1.0.0"
        },
        "basePath": "/"
    })

    # Register Blueprints
    from app.routes.file_routes import file_bp
    app.register_blueprint(file_bp, url_prefix="/api/files")

    from app.routes.record_routes import record_bp
    app.register_blueprint(record_bp, url_prefix="/api/records")

    from app.extensions.celery import init_celery
    init_celery(app)

    return app
