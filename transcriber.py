import os
from file_manager import FileManager

class Transcriber:

    BASE_RESOURCE_PATH = "tasks_resources/transcribe/"

    @classmethod
    def audio_file_path(cls, task, audio_file):
        if not task or not audio_file or not audio_file.filename:
            return None

        _, extension = os.path.splitext(audio_file.filename)
        file_path = os.path.join(cls.get_task_base_path(task), f"audio.{extension}")

        return file_path

    @classmethod
    def get_result(cls, task):
        if not task:
            return None
        result_file_path = os.path.join(cls.get_task_base_path(task), "transcription.json")
        result = FileManager.get_file_content(result_file_path)

        return result

    @classmethod
    def get_task_base_path(cls, task):
        return os.path.join(cls.BASE_RESOURCE_PATH, str(task.id))

