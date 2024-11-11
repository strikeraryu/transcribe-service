from flask import Flask
from flask_cors import CORS
from apis.core import core_bp
from apis.transcribe import transcribe_bp
from models import Task, db
from flask_migrate import Migrate
import logging
from celery import Celery
from celery.schedules import crontab
from celery_app.celery_tasks import poll_and_process_tasks
import os

# Setup App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'I am a big secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAX_FORM_MEMORY_SIZE'] = 16 * 1024 * 1024
app.config['broken_url'] = 'redis://localhost:6379/0'
app.config['result_backend'] = 'redis://localhost:6379/0'

db.init_app(app)
migrate = Migrate(app, db)

# Setup CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register blueprints
app.register_blueprint(core_bp)
app.register_blueprint(transcribe_bp, url_prefix='/transcribe')

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broken_url']
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    celery.conf.beat_schedule = {
        'poll-every-minute': {
            'task': 'celery_app.celery_tasks.poll_and_process_tasks',
            'schedule': crontab(minute='*'),  # Runs every minute
        },
    }

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)
__all__ = ['celery']

if __name__ == '__main__':
    # gunicorn_logger = logging.getLogger('gunicorn.error')
    # app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)    
    app.run(debug=True)
