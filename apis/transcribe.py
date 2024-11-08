from flask import Blueprint, request, jsonify
from audio_file_manager import AudioFileManager
from models import Task, db
import traceback
import os

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"success": False, "message": 'No audio file provided'}), 400

        audio_file = request.files.get('audio')
        file_name = f"audio.{audio_file.filename.split('.')[-1]}"
        task = Task(file_name=file_name, status=Task.Status.QUEUED, action_type=Task.ActionType.TRANSCRIBE)
        db.session.add(task)
        db.session.commit()

        task_dir = os.path.join("task_data", str(task.id))
        file_path = os.path.join(task_dir, file_name)
        os.makedirs(task_dir, exist_ok=True)

        AudioFileManager.upload_file(audio_file, filename=file_name)

        return jsonify({"success": True, "task_id": task.id}), 200
    except Exception as e:
        print("Error occurred in transcribe API: ", e)
        print(traceback.format_exc())

        return jsonify({"success": False, "message": "Something went wrong"}), 500
