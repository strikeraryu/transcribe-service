from flask import Blueprint, request, jsonify, send_from_directory
from audio_file_manager import AudioFileManager
from models import Task, db
from celery_app.celery_tasks import process_task
import traceback
import os

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"success": False, "message": 'No audio file provided'}), 400

        audio_file = request.files.get('audio')

        allowed_extensions = {'mp3', 'wav', 'ogg'}
        if '.' not in audio_file.filename or audio_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({"success": False, "message": "Unsupported file type"}), 400

        file_name = f"audio.{audio_file.filename.split('.')[-1]}"
        task = Task(file_name=file_name, status=Task.Status.QUEUED, action_type=Task.ActionType.TRANSCRIBE)
        db.session.add(task)
        db.session.commit()

        task_dir = os.path.join("task_data", str(task.id))
        file_path = os.path.join(task_dir, file_name)
        os.makedirs(task_dir, exist_ok=True)

        AudioFileManager.upload_file(audio_file, filename=file_name, file_path=file_path)

        # Queue the task
        process_task.apply_async(args=[task.id])

        return jsonify({"success": True, "task_id": task.id}), 200
    except Exception as e:
        print("Error occurred in transcribe API: ", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Something went wrong"}), 500

@transcribe_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "Task Not Found"}), 404

        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True, "message": "Task deleted successfully"}), 200
    except Exception as e:
        print("Error occurred in delete_task API: ", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Something went wrong"}), 500

@transcribe_bp.route('/<int:task_id>/result', methods=['GET'])
def get_task_output(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "Task Not Found"}), 404

        if task.status != Task.Status.COMPLETED:
            print(task.Status)
            return jsonify({"success": False, "message": "Task Not Completed"}), 400

        task_dir = os.path.join("task_data", str(task_id))

        files = os.listdir(task_dir)
        if not files:
            return jsonify({"success": False, "message": "Output file not found"}), 404

        output_file = files[0]
        
        return send_from_directory(task_dir, output_file, as_attachment=True)
    except Exception as e:
        print("Error occurred in get_task_output API: ", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Something went wrong"}), 500