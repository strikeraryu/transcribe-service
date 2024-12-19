import os
import boto3

class S3Client:
    def __init__(self, region_name, bucket_name):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=region_name
        )
        self.bucket_name = bucket_name

    def upload_file_obj(self, file, file_path):
        return self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            file_path
        )

    def upload_file(self, file, file_path):
        return self.s3_client.upload_file(
            file,
            self.bucket_name,
            file_path
        )

    def get_file_obj(self, file_key):
        return self.s3_client.get_object(
            Bucket=self.bucket_name, Key=file_key
        )

    def download_file(self, file_key, file_path):
            return self.s3_client.download_file(self.bucket_name, file_key, file_path)
