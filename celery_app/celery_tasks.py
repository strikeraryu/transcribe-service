from celery import shared_task
from models import db, Task
import time
import traceback
import docker
import os
import asyncio
import json
from functools import wraps
import redis
from contextlib import contextmanager

class WorkerManager:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        # Initialize Redis client
        self.redis_client = redis.Redis(
            host='localhost',  # Your local Redis host
            port=6379,
            db=1  # Use a different DB than Celery
        )
        
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"Failed to initialize Docker client: {str(e)}")
            raise

    def get_active_workers(self):
        count = self.redis_client.get('active_workers')
        return int(count or 0)

    def can_accept_task(self):
        print(self.get_active_workers())
        return self.get_active_workers() < self.max_workers

    @contextmanager
    def worker_context(self):
        """Context manager for tracking worker count"""
        try:
            # Atomic increment
            self.redis_client.incr('active_workers')
            yield
        finally:
            # Atomic decrement
            self.redis_client.decr('active_workers')

    async def run_transcription_container(self, task_id, audio_file_path):
        try:
            # Ensure absolute paths for volume bindings
            host_task_data = os.path.abspath('task_data')
            
            # Environment variables for the container
            environment = {
                'NVIDIA_VISIBLE_DEVICES': 'all',
                'REDIS_HOST': 'host.docker.internal',  # Allows container to access host's Redis
                'REDIS_PORT': '6379'
            }

            # Device requests for GPU
            device_requests = [
                docker.types.DeviceRequest(
                    count=-1,
                    capabilities=[['gpu']]
                )
            ]
            
            volumes = {
                host_task_data: {
                    'bind': '/app/task_data',
                    'mode': 'rw'
                }
            }

            # Add extra_hosts to allow container to reach host's Redis
            extra_hosts = {'host.docker.internal': 'host-gateway'}

            container = self.docker_client.containers.run(
                'transcription-worker',
                command=[
                    'python', '-c',
                    f'from helpers.transcribe_helper import transcribe_and_store_single_file; '
                    f'result = transcribe_and_store_single_file("{audio_file_path}", "/app/task_data/results_{task_id}.json")'
                ],
                volumes=volumes,
                environment=environment,
                device_requests=device_requests,
                extra_hosts=extra_hosts,
                detach=True,
                remove=True,
                user='worker'
            )

            # Monitor container status
            start_time = time.time()
            print(f"Started container for task {task_id}")
            
            while True:
                try:
                    container.reload()
                    if container.status == 'exited':
                        print(f"Container for task {task_id} completed")
                        break
                        
                    if time.time() - start_time > 600:  # 10 minute timeout
                        print(f"Container for task {task_id} timed out")
                        container.stop(timeout=2)
                        raise TimeoutError("Transcription timed out after 10 minutes")
                        
                    await asyncio.sleep(1)
                    
                except docker.errors.NotFound:
                    print(f"Container for task {task_id} not found")
                    break

            result_path = f"task_data/results_{task_id}.json"
            if os.path.exists(result_path):
                with open(result_path, 'r') as f:
                    return json.load(f)
            return None

        except Exception as e:
            print(f"Container execution error for task {task_id}: {str(e)}")
            traceback.print_exc()
            raise

def with_worker_management(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        task_id = args[1] if len(args) > 1 else kwargs.get('task_id')
        manager = WorkerManager()
        
        if not manager.can_accept_task():
            print(f"Max workers reached, requeueing task {task_id}")
            process_task.apply_async(args=[task_id], countdown=30)
            return

        with manager.worker_context():
            return f(*args, **kwargs)
    return wrapper

@shared_task(bind=True, max_retries=3)
@with_worker_management
def process_task(self, task_id):
    task = None
    manager = WorkerManager()

    try:
        print(f"Processing task {task_id} with {manager.get_active_workers()} active workers")
        task = Task.query.get(task_id)
        if not task or task.status not in [Task.Status.QUEUED, Task.Status.RUNNING]:
            return

        task.status = Task.Status.RUNNING
        db.session.commit()

        audio_file_path = os.path.join("task_data", str(task_id), task.file_name)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            transcription_result = loop.run_until_complete(
                manager.run_transcription_container(task_id, audio_file_path)
            )
        finally:
            loop.close()

        if transcription_result:
            task.result = transcription_result
            task.status = Task.Status.COMPLETED
        else:
            handle_task_error(task, self)

        db.session.commit()

    except TimeoutError:
        print(f"Task {task_id} timed out")
        handle_task_error(task, self, is_timeout=True)
    except Exception as e:
        print(f"Error in process_task: {str(e)}")
        if task:
            handle_task_error(task, self)
        raise