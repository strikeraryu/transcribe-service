class AudioFileManager():

    @classmethod
    def upload_file(cls, audio_file, filename=None):
        filename = filename or audio_file.filename
        audio_file.save(f'./uploads/{filename}')
