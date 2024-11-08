from celery import shared_task
from models import db, Task
from helpers.transcribe_helper import transcribe_and_store_single_file
import traceback
import os

@shared_task(bind=True)
def poll_and_process_tasks(self):
    running_tasks_count = Task.query.filter_by(status=Task.Status.RUNNING).count()
    max_concurrent_tasks = 4

    tasks_to_pick = max_concurrent_tasks - running_tasks_count
    if tasks_to_pick <= 0:
        return

    queued_tasks = Task.query.filter_by(status=Task.Status.QUEUED).limit(tasks_to_pick).all()
    
    for task in queued_tasks:
        process_task.delay(task.id)

@shared_task(bind=True)
def process_task(self, task_id):
    task = Task.query.get(task_id)
    if not task or task.status != Task.Status.QUEUED:
        return

    try:
        task.status = Task.Status.RUNNING
        db.session.commit()

        audio_file_path = os.path.join("task_data", str(task.id), task.file_name)
        print(audio_file_path)
        transcription_result = transcribe_and_store_single_file(audio_file_path, "task_data/results.json")
        
        if transcription_result:
            task.result = transcription_result
            task.status = Task.Status.COMPLETED
        else:
            task.retry_count += 1
            if task.retry_count >= 3:
                task.status = Task.Status.FAILED
            else:
                task.status = Task.Status.QUEUED

        db.session.commit()

    except Exception as e:
        print("Error occurred in task processing:", e)
        print(traceback.format_exc())

        task.retry_count += 1
        if task.retry_count >= 3:
            task.status = Task.Status.FAILED
        else:
            task.status = Task.Status.QUEUED
        db.session.commit()
