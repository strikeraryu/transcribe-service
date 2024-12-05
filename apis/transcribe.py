from flask import Blueprint, request, jsonify, send_from_directory
from file_manager import FileManager
from transcriber import Transcriber
from models import Task, db
from celery_app.celery_tasks import process_task
import traceback
import os

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/', methods=['POST'])
def transcribe():
    try:
        audio_file = request.files.get('audio')

        if not audio_file:
            return jsonify({"success": False, "message": 'No audio file provided'}), 400

        if not FileManager.validate_audio_file(audio_file.filename):
            return jsonify({"success": False, "message": "Unsupported file"}), 400

        task = Task()
        db.session.add(task)
        db.session.commit()

        try: 

            file_path = Transcriber.audio_file_path(task, audio_file)
            FileManager.upload_file(audio_file, file_path)

            # Queue the task
            # process_task.apply_async(args=[task.id])

            return jsonify({"success": True, "task_id": task.id}), 200

        except Exception as e:
            task.status = Task.Status.FAILED
            task.message = str(e)
            db.session.commit()

            print("Error occurred in transcribe API: ", e)

            return jsonify({"success": False, "message": "Something went wrong"}), 500
    except Exception as e:
        print("Error occurred in transcribe API: ", e)

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

        return jsonify({"success": False, "message": "Something went wrong"}), 500

@transcribe_bp.route('/<int:task_id>/result', methods=['GET'])
def get_task_output(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"success": False, "message": "Task Not Found"}), 404

        result = Transcriber.get_result(task)
        response = {
            'success': True,
            'status': task.status,
            'result': result
        }

        return jsonify(response), 200
    except Exception as e:
        print("Error occurred in get_task_output API: ", e)
        print(traceback.format_exc())
        return jsonify({"success": False, "message": "Something went wrong"}), 500
