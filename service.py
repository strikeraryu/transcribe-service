from flask import Flask
from flask_cors import CORS
from apis.core import core_bp
from apis.transcribe import transcribe_bp
from models import Task, db
from flask_migrate import Migrate
import logging
import os
from celery_app import init_celery

# Setup App
app = Flask(__name__)

app.config.update(
    SECRET_KEY='I am a big secret',
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///app.db'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    MAX_FORM_MEMORY_SIZE=16 * 1024 * 1024,
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TIMEZONE='UTC',
    CELERY_ENABLE_UTC=True,
)

db.init_app(app)
migrate = Migrate(app, db)

# Setup CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register blueprints
app.register_blueprint(core_bp)
app.register_blueprint(transcribe_bp, url_prefix='/transcribe')

# Initialize Celery
celery = init_celery(app)

if __name__ == '__main__':
    app.run(debug=True)