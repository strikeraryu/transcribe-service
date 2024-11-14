class AudioFileManager():

    @classmethod
    def upload_file(cls, audio_file, filename=None, file_path=None):
        filename = filename or audio_file.filename
        file_path = file_path or os.path.join('./uploads', filename)
        
        audio_file.save(file_path)
