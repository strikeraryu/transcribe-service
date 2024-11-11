import subprocess
import os

class TranscribeWrapper:
    ARGS = [
        "model",
        "device",
        "dtype",
        "batch-size",
        "chunk-length"
    ]
    def __init__(self, model=None, device=None, dtype=None, batch_size=None, chunk_length=None):
        """
        Initialize the WhisperWrapper with customizable parameters for the CLI tool.
        """
        self.model = model
        self.device = device
        self.dtype = dtype
        self.batch_size = batch_size
        self.chunk_length = chunk_length

    def transcribe(self, audio_file, output_file="output.srt"):
        """
        Transcribe the audio file using insanely-fast-whisper CLI and save the result in the specified output file.
        """
        command = ["pipx", "run", "insanely-fast-whisper"]

        for arg in self.ARGS:
            value = getattr(self, arg.replace("-", "_"))
            if value is not None:
                command.extend(["--"+arg, str(value)])

        transcription_file = "transcription.json"
        command += ["--file-name", audio_file]
        command += ["--transcript-path", transcription_file]

        with open(output_file, "w") as output:
            try:
                # Run the CLI command and redirect the output to the file
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

    def set_model(self, model):
        """Set the ASR model."""
        self.model = model

    def set_device(self, device):
        """Set the computation device."""
        self.device = device

    def set_dtype(self, dtype):
        """Set the data type."""
        self.dtype = dtype

    def set_batch_size(self, batch_size):
        """Set the batch size for transcription."""
        self.batch_size = batch_size

    def set_chunk_length(self, chunk_length):
        """Set the chunk length for processing."""
        self.chunk_length = chunk_length
