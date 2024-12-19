import subprocess
import json
import time
import random
import os
from libs.file_manager import FileManager


class TranscriberModelMock:
    ARGS = {
        "model": "model",
        "device-id": "device_id",
        "batch-size": "batch_size",
        "language": "language",
    }

    def __init__(
            self, model=None, device_id=None, batch_size=None, 
        language="english", mock_config={'success_rate': 0.6, 'error_rate': 0.1, 'max_delay': 100, 'min_delay': 10}
    ):
        self.model = model
        self.device_id = device_id
        self.batch_size = batch_size
        self.language = language
        self.mock_config = mock_config
    
    def transcribe(self, audio_file, output_file=None):
        command = ["pipx", "run", "insanely-fast-whisper"]
        
        for arg in self.ARGS:
            arg_var = self.ARGS[arg]
            arg_value = getattr(self, arg_var, None)
            if arg_value is not None:
                command.extend([f"--{arg}", str(arg_value)])
              

        if not output_file:
            unix_time_stamp = int(time.time())
            output_file = f"{unix_time_stamp}"

        command.extend(["--file-name", audio_file])
        command.extend(["--transcript-path", output_file])

        success, result = False, {}
        
        try:
            response = self.mock_run(command)
            if response.returncode != 0:
                print(f"Error transcribing audio: {response.stderr}")
                result["message"] = response.stderr
                result["success"] = False
            else:
                success = True
                result["message"] = response.stdout
                result["success"] = success
                result["output_file"] = output_file
        except Exception as e:
            print(f"Failed to transcribe audio: {str(e)}")
            result["message"] = str(e)
            result["success"] = False

        return result

    def mock_run(self, command):
        print(f"Running command: {command}")

        audio_file_path = command[command.index('--file-name') + 1]

        if not os.path.exists(audio_file_path) and FileManager.validate_audio_file(audio_file_path):
            raise Exception("Audio file not found.")

        # Simulate processing time
        time.sleep(random.uniform(0, self.mock_config['max_delay']))

        # Determine outcome based on mock_config
        outcome = random.choices(
            ['success', 'failure', 'error'], 
            weights=[
                self.mock_config['success_rate'], 
                1 - self.mock_config['success_rate'] - self.mock_config['error_rate'],
                self.mock_config['error_rate']]
        )[0]

        if outcome == 'success':
            # Create a mock transcript file
            transcript_path = command[command.index('--transcript-path') + 1]
            response = {
                    "speakers": [],
                    "chunks": [ { "timestamp": [ 0.0, 4.0 ], "text": " The stale smell of old beer lingers." } ],
                    "text": " The stale smell of old beer lingers."
                }

            with open(transcript_path, 'w') as f:
                json.dump(response, f)

            return MockResponse(stdout="Transcription successful.", stderr="", returncode=0)

        elif outcome == 'failure':
            return MockResponse(stdout="", stderr="Transcription failed due to an unknown error.", returncode=1)

        raise Exception("An error occurred during transcription.")

class MockResponse:
    def __init__(self, stdout, stderr, returncode):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
