from celery import Celery

celery = Celery(
    'celery_app',
    include=['celery_app.celery_tasks']
)

def init_celery(app=None):
    """Initialize celery with Flask app configurations"""
    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery