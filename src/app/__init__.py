from flask import Flask
from app.extensions.db import db
from app.extensions.celery import celery
from app.routes.file_routes import file_bp
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from .config import Config
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    celery.conf.update(app.config)
    
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "File Upload API",
            "description": "Multi-provider file upload API with S3 and Azure support",
            "version": "1.0.0"
        },
        "basePath": "/"
    })

    # Register Blueprints
    from app.routes.file_routes import file_bp
    app.register_blueprint(file_bp, url_prefix="/api/files")

    from app.extensions.celery import init_celery
    init_celery(app)

    return app
