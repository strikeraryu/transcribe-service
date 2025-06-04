import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime
import time
import random
from rich.console import Console
from rich.live import Live
from rich.table import Table
from pydub import AudioSegment
import pandas as pd
import contextlib

class TranscriptionLoadTest:
    def __init__(self, base_url, audio_files_dir, total_requests=100, batch_size=10):
        self.base_url = base_url
        self.audio_files_dir = Path(audio_files_dir)
        self.total_requests = total_requests
        self.batch_size = batch_size
        self.results = []
        self.metrics = {"initiated": 0, "completed": 0, "failed": 0}
        self.console = Console()
        self.start_time = None

    def generate_metrics_table(self):
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        table.add_row("Time Elapsed", f"{elapsed:.1f}s")
        table.add_row("Completed", str(self.metrics["completed"]))
        table.add_row("Failed", str(self.metrics["failed"]))
        return table

    async def process_audio(self, session, audio_file):
        test_id = random.randint(10000, 99999)
        start_time = time.time()
        
        try:
            with open(audio_file, 'rb') as f:
                file_content = f.read()
            
            audio = AudioSegment.from_file(audio_file)
            duration = len(audio) / 1000

            mpwriter = aiohttp.MultipartWriter('form-data')
            part = mpwriter.append(file_content)
            part.set_content_disposition('form-data', name='audio', filename=audio_file.name)

            async with session.post(f"{self.base_url}/transcribe", data=mpwriter) as response:
                if response.status != 200:
                    self.metrics["failed"] += 1
                    return self._create_result(test_id, audio_file.name, False, None, duration, f"HTTP {response.status}")

                data = await response.json()
                result = await self._poll_result(session, data['task_id'], start_time, audio_file.name, test_id, duration)
                return result

        except Exception as e:
            self.metrics["failed"] += 1
            return self._create_result(test_id, str(audio_file), False, None, duration, str(e))

    async def _poll_result(self, session, task_id, start_time, filename, test_id, duration):
        while True:
            try:
                async with session.get(f"{self.base_url}/transcribe/{task_id}/result") as response:
                    if response.status != 200:
                        self.metrics["failed"] += 1
                        return self._create_result(test_id, filename, False, None, duration, f"HTTP {response.status}")

                    data = await response.json()
                    if data['status'] == 'COMPLETED':
                        self.metrics["completed"] += 1
                        return self._create_result(test_id, filename, True, time.time() - start_time, duration, None, len(data['result']))
                    
                    if data['status'] == 'FAILED':
                        self.metrics["failed"] += 1
                        return self._create_result(test_id, filename, False, time.time() - start_time, duration, 'Transcription failed')

                    await asyncio.sleep(2)

            except Exception as e:
                self.metrics["failed"] += 1
                return self._create_result(test_id, filename, False, None, duration, str(e))

    def _create_result(self, test_id, filename, success, completion_time, duration, error=None, content=None):
        return {
            'test_id': test_id,
            'file_name': filename,
            'success': success,
            'completion_time': completion_time,
            'duration_seconds': duration,
            'error': error,
            'content': content
        }

    async def run_load_test(self):
        audio_files = list(self.audio_files_dir.glob('*.mp3'))
        self.start_time = time.time()

        async with aiohttp.ClientSession() as session:
            with Live(self.generate_metrics_table(), refresh_per_second=1) as live:
                async def update_metrics():
                    while True:
                        live.update(self.generate_metrics_table())
                        await asyncio.sleep(1)

                metrics_task = asyncio.create_task(update_metrics())

                try:
                    for i in range(0, self.total_requests, self.batch_size):
                        batch = [random.choice(audio_files) for _ in range(min(self.batch_size, self.total_requests - i))]
                        results = await asyncio.gather(*(self.process_audio(session, file) for file in batch))
                        self.results.extend(results)
                        await asyncio.sleep(1)  # Rate limiting between batches
                finally:
                    metrics_task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await metrics_task

    def generate_report(self):
        df = pd.DataFrame(self.results)
        completion_times = df[df['success']]['completion_time'].dropna()
        
        report = {
            'total_requests': len(self.results),
            'success_rate': (df['success'].sum() / len(self.results) * 100),
            'avg_time': completion_times.mean() if not completion_times.empty else 0,
            'p95_time': completion_times.quantile(0.95) if not completion_times.empty else 0,
            'failed_breakdown': df[~df['success']]['error'].value_counts().to_dict()
        }
        
        df.to_csv(f'load_test_results_{int(time.time())}.csv', index=False)
        return report

async def main():
    BASE_URL = "https://fast-transcriber.sales-copilot.scaler.com/"
    AUDIO_FILES_DIR = "./audio_files"
    TOTAL_REQUESTS = 1
    BATCH_SIZE = 20

    load_tester = TranscriptionLoadTest(
        base_url=BASE_URL,
        audio_files_dir=AUDIO_FILES_DIR,
        total_requests=TOTAL_REQUESTS,
        batch_size=BATCH_SIZE
    )
    
    await load_tester.run_load_test()
    report = load_tester.generate_report()
    
    console = Console()
    console.print("\n[bold]Test Results[/bold]")
    console.print(f"Success Rate: {report['success_rate']:.1f}%")
    console.print(f"Average Time: {report['avg_time']:.1f}s")
    console.print(f"P95 Time: {report['p95_time']:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
