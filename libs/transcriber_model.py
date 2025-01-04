import subprocess
import time


class TranscriberModel:
    ARGS = {
        "model": "model",
        "device-id": "device_id",
        "batch-size": "batch_size",
        "language": "language",
    }

    def __init__(self, model=None, device_id=None, batch_size=None, language="english"):
        self.model = model
        self.device_id = device_id
        self.batch_size = batch_size
        self.language = language
    
    def transcribe(self, audio_file, output_file=None):
        command = ["insanely-fast-whisper"]
        
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
            response = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
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
