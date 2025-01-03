import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from apis.core import core_bp
from apis.transcribe import transcribe_bp
from models import db
from celery_app import init_celery

# Setup App
app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.getenv('APP_SECRET_KEY'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    MAX_FORM_MEMORY_SIZE=16 * 1024 * 1024,
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL'),
    CELERY_RESULT_BACKEND=None,
    CELERY_TASK_IGNORE_RESULT=True
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
