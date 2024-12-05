import os

class FileManager():

    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}

    @classmethod
    def upload_file(cls, audio_file, file_path):
        audio_file.save(file_path)

    @classmethod
    def get_file_content(cls, filename):
        if filename is None or not os.path.exists(filename):
            return None

        with open(filename, 'rb') as f:
            return f.read()

    @classmethod
    def validate_audio_file(cls, filename):
        if not filename or '.' not in filename:
            return False

        _, extension = os.path.splitext(filename)

        return extension in cls.ALLOWED_EXTENSIONS
