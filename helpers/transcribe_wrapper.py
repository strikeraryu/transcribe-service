import subprocess
import os
import json

class TranscribeWrapper:
    ARGS = [
        "model",
        "device",
        "dtype",
        "batch-size",
        "chunk-length"
    ]
    
    def __init__(self, model=None, device="cuda", dtype="float16", batch_size=8, chunk_length=30):
        self.model = model
        self.device = device
        self.dtype = dtype
        self.batch_size = batch_size
        self.chunk_length = chunk_length
    
    def transcribe(self, audio_file, output_file="output.srt"):
        command = ["pipx", "run", "insanely-fast-whisper"]
        
        # Always include GPU-related parameters
        command.extend(["--device", "cuda"])
        command.extend(["--dtype", "float16"])  # Use float16 for better GPU performance
        command.extend(["--batch-size", str(self.batch_size)])
        
        # Add other parameters if specified
        if self.model:
            command.extend(["--model", str(self.model)])
        if self.chunk_length:
            command.extend(["--chunk-length", str(self.chunk_length)])
            
        transcription_file = "transcription.json"
        command.extend(["--file-name", audio_file])
        command.extend(["--transcript-path", transcription_file])
        
        with open(output_file, "w") as output:
            try:
                result = subprocess.run(command, stdout=output, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    print(f"Error: {result.stderr}")
                    return None
            except Exception as e:
                print(f"Failed to transcribe audio: {str(e)}")
                return None
                
        with open(transcription_file, "r") as f:
            transcription_text = json.load(f)
        return transcription_text