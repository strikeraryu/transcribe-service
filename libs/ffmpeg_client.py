import subprocess
import os

class FfmpegClient:
    def __init__(self):
        # Check if ffmpeg is installed
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError("ffmpeg is not installed or not found in system PATH")

    def encode_to_mp3(self, video_file, audio_file, quality=2):
        if not os.path.exists(video_file):
            return False, f"Input video file not found: {video_file}"

        try:
            # Run ffmpeg command
            command = [
                'ffmpeg',
                '-i', video_file,  # Input file
                '-q:a', str(quality),       # Audio quality (2 is high quality)
                '-y',              # Overwrite output file if it exists
                audio_file         # Output file
            ]

            subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            
            if os.path.exists(audio_file):
                return True, "Audio file created successfully"
            else:
                return False, "Failed to create audio file"
                
        except subprocess.SubprocessError as e:
            return False, str(e)
