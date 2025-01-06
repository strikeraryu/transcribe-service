import os
from celery import Celery

QUEUE_NAME = os.getenv('QUEUE_NAME', 'transcribe-queue')
celery_app = Celery(
    'celery_app',
    broker=os.getenv('CELERY_BROKER_URL'),
    backend=None,
    task_ignore_result=True,
    task_default_queue=QUEUE_NAME,
    task_routes={
        'tasks.transcribe_tasks.transcribe_task': {'queue': QUEUE_NAME},
    },
    broker_transport_options={
        'region': os.getenv('AWS_REGION'),
        'predefined_queues': {
            QUEUE_NAME: {
                'url': os.getenv('SQS_QUEUE_URL')
            }
        },
        'visibility_timeout': 3600
    },
    worker_prefetch_multiplier = 1,
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
