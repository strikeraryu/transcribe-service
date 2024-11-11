import subprocess
import os
import json
import time
from datetime import datetime
from helpers.transcribe_wrapper import TranscribeWrapper
from pydub import AudioSegment

model = "distil-whisper/distil-large-v3"
whisper = TranscribeWrapper(model=model)
output_json = "transcription_results.json"


def transcribe_and_store_single_file(audio_file, output_json):
    try:
        # Start processing
        start_time = time.time()
        print(f"Processing {audio_file}")
        
        # Transcribe audio
        transcription_text = whisper.transcribe(audio_file)
        print("Processed")
        
        # Measure processing time
        end_time = time.time()

        # Calculate audio duration
        audio = AudioSegment.from_mp3(audio_file)
        duration = len(audio) / 1000

        # Load existing results or create a new dictionary
        if os.path.exists(output_json):
            with open(output_json, "r") as f:
                results = json.load(f)
        else:
            results = {}

        results["logs"] = results.get("logs", [])

        # Append transcription results to logs
        results["logs"].append({
            "file_path": audio_file,
            "duration": duration,
            "time_taken": int(end_time - start_time),
            "time": str(datetime.now()),
            "model": model,
            "transcription": transcription_text
        })

        # Save updated results to JSON file
        with open(output_json, "w+") as f:
            json.dump(results, f, indent=4)

    except Exception as e:
        print(f"Error processing {audio_file}: {e}")