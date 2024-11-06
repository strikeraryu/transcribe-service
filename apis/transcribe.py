from flask import Blueprint, request, jsonify
from audio_file_manager import AudioFileManager
from models import Job, db
import traceback

import os

transcribe_bp = Blueprint('transcribe', __name__)

@transcribe_bp.route('/', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({"success": False, "message": 'No audio file provided'}), 400

        audio_file = request.files.get('audio')

        # file_name = f"audio.{audio_file.filename.split('.')[-1]}"
        # job = Job(file_name=file_name, status=Job.Status.QUEUED, job_type=Job.ActionType.TRANSCRIBE)
        # db.session.add(job)
        # db.session.commit()

        # job_dir = os.path.join("job_data", str(job.id))
        # file_path = os.path.join(job_dir, file_name)
        # os.makedirs(job_dir, exist_ok=True)

        AudioFileManager.upload_file(audio_file, filename=audio_file.filename)

        return jsonify({"success": True, "job_id": 1}), 200
    except Exception as e:
        print("Error occurred in transcribe API: ", e)
        print(traceback.format_exc())

        return jsonify({"success": False, "message": "Something went wrong"}), 500
