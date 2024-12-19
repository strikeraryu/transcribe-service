import os
import json
import time
import shutil

from botocore.parsers import RestJSONParser
from libs.file_manager import FileManager
from libs.transcriber_model import TranscriberModel
from libs.transcriber_model_mock import TranscriberModelMock

class Transcriber:

    BASE_RESOURCE_PATH = "resources/transcribe/"
    MODEL_NAME = "openai/whisper-large-v3-turbo"
    TRANSCRIPTION_FILE_NAME = "transcription.json"

    @classmethod
    def transcribe(cls, task):
        if not task:
            return [False, "Task not found"]

        file_key = task.audio_file
        unix_time_stamp = int(time.time())
        task_id = task.id
        file_dir = f"./tmp/{unix_time_stamp}{task_id}/"

        # Create the directory if it doesn't exist
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        FileManager.download_audio_file(file_key, file_dir)
        audio_file_path = os.path.join(file_dir, os.path.basename(file_key))
        success, message = True, ""

        if success:
            transcriber_model = TranscriberModelMock(model=cls.MODEL_NAME)
            transcription_result = transcriber_model.transcribe(
                audio_file=audio_file_path, output_file=os.path.join(file_dir, cls.TRANSCRIPTION_FILE_NAME)
            )

            if transcription_result["success"]:
                FileManager.upload_file(transcription_result["output_file"], cls.result_file_path(task), obj=False)

                success, message = True, transcription_result["message"]
            else: 
                success, message = False, transcription_result["message"]

        last_result_path = os.path.join(file_dir, "last_result.json")
        with open(last_result_path, 'w') as file:
            json.dump({"success": success, "message": message}, file)


        FileManager.upload_file(last_result_path, os.path.join(cls.get_task_base_path(task), "last_result.json"), obj=False)

        shutil.rmtree(file_dir)

        return [success, message]

    @classmethod
    def audio_file_path(cls, task, audio_file):
        if not task or not audio_file or not audio_file.filename:
            return None

        _, extension = os.path.splitext(audio_file.filename)
        file_path = os.path.join(cls.get_task_base_path(task), f"audio{extension}")

        return file_path

    @classmethod
    def result_file_path(cls, task):
        if not task:
            return None

        result_file_path = os.path.join(cls.get_task_base_path(task), cls.TRANSCRIPTION_FILE_NAME)

        return result_file_path

    @classmethod
    def get_result(cls, task):
        if not task:
            return None

        result_file_path = cls.result_file_path(task)
        result = FileManager.get_file_content(result_file_path)

        return result

    @classmethod
    def get_task_base_path(cls, task):
        return os.path.join(cls.BASE_RESOURCE_PATH, str(task.id))

