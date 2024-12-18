import logging
from celery_app import celery_app
from models import Task
from libs.transcriber import Transcriber
from models import db

# Configure logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, autoretry_for=(Exception,), max_retries=5, default_retry_delay=10)
def transcribe_task(self, task_id):
    logger.debug(f'Starting transcribe_task for task_id: {task_id}')
    task = Task.query.get(task_id)
    if not task:
        logger.info(f'Task with id {task_id} not found.')
        return True
    
    try:
        task.status = Task.Status.RUNNING
        db.session.commit()
        logger.info(f'Task {task_id} status set to RUNNING.')
        
        success, message = Transcriber.transcribe(task)
        
        if success:
            task.status = Task.Status.COMPLETED
            task.message = message
            logger.info(f'Task {task_id} completed successfully.')
        else:
            task.retry_count += 1
            task.message = message
            task.status = Task.Status.QUEUED
            logger.info(f'Task {task_id} failed with message: {message}. Retrying...')
            raise Exception(message)
        
        db.session.commit()
        return True
    
    except Exception as exc:
        logger.error(f'Error processing task {task_id}: {exc}')
        # Only retry if we haven't hit max retries
        if self.request.retries < self.max_retries:
            task.status = Task.Status.QUEUED
            task.message = str(exc)
            db.session.commit()
            logger.info(f'Retrying task {task_id}. Retry count: {self.request.retries}')
            raise self.retry(exc=exc)
        else:
            task.status = Task.Status.FAILED
            task.message = str(exc)
            db.session.commit()
            logger.error(f'Task {task_id} failed after max retries.')
            raise
