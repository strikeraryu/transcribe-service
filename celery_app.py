import os
from celery import Celery

celery_app = Celery(
    'celery_app',
    task_routes={
        'tasks.transcribe_tasks.transcribe_task': {'queue': 'default'},
    },
    worker_concurrency=int(os.getenv('CELERY_WORKER_CONCURRENCY', 2))
)

def init_celery(app=None):
    """Initialize celery with Flask app configurations"""
    if app:
        celery_app.conf.update(app.config)

        class ContextTask(celery_app.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app.Task = ContextTask

    return celery_app
