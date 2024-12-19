import os
from libs.s3_client import S3Client

class FileManager():

    ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.ogg'}
    s3_client = S3Client(
        os.getenv('AWS_REGION'),
        os.getenv('AWS_S3_BUCKET_NAME')
    )

    @classmethod
    def upload_file(cls, file, file_path, obj=True):
        if obj:
            cls.s3_client.upload_file_obj(file, file_path)
        else:
            cls.s3_client.upload_file(file, file_path)

    @classmethod
    def get_file_content(cls, file_key):
        if not file_key:
            return None

        response = cls.s3_client.get_file_obj(file_key)
        return response['Body'].read().decode('utf-8')

    @classmethod
    def download_audio_file(cls, file_key, file_dir):
        file_path = os.path.join(file_dir, os.path.basename(file_key))

        # Create missing directories
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        return cls.s3_client.download_file(file_key, file_path)

    @classmethod
    def validate_audio_file(cls, filename):
        if not filename or '.' not in filename:
            return False

        _, extension = os.path.splitext(filename)

        return extension in cls.ALLOWED_EXTENSIONS
