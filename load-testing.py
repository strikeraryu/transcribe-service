import asyncio
import aiohttp
import time
import random
import json
from pathlib import Path
import statistics
from datetime import datetime
from pydub import AudioSegment
import pandas as pd
from rich.console import Console
from rich.live import Live
from rich.table import Table
import logging
import contextlib

class TranscriptionLoadTest:
    def __init__(self, base_url, audio_files_dir, total_requests=100, concurrent_requests=5, rate_limit=10, max_retries=1800):
        self.base_url = base_url
        self.audio_files_dir = Path(audio_files_dir)
        self.total_requests = total_requests
        self.concurrent_requests = concurrent_requests
        self.rate_limit = rate_limit  # requests per second
        self.max_retries = max_retries
        self.results = []
        self.metrics = {
            "initiated": 0,
            "completed": 0,
            "failed": 0,
            "in_progress": 0
        }
        self.console = Console()
        self.start_time = None

    def generate_metrics_table(self):
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        table.add_row("Time Elapsed", f"{elapsed:.1f}s")
        table.add_row("In Progress", str(self.metrics["initiated"] - self.metrics["completed"] - self.metrics["failed"]))
        table.add_row("Completed", str(self.metrics["completed"]))
        table.add_row("Failed", str(self.metrics["failed"]))
        return table

    async def submit_transcription(self, session, audio_file):
        start_time = time.time()
        test_id = random.randint(10000, 99999)
        
        self.metrics["initiated"] += 1
        
        try:
            with open(audio_file, 'rb') as f:
                file_content = f.read()
                file_name = audio_file.name

            audio = AudioSegment.from_file(audio_file) 
            duration_seconds = len(audio) / 1000  

            with aiohttp.MultipartWriter('form-data') as mpwriter:
                part = mpwriter.append(file_content)
                part.set_content_disposition('form-data', name='audio', filename=file_name)
                
                async with session.post(f"{self.base_url}/transcribe", data=mpwriter) as response:
                    if response.status != 200:
                        self.metrics["failed"] += 1
                        return {
                            'test_id': test_id,
                            'file_name': file_name,
                            'duration_seconds': duration_seconds,
                            'success': False,
                            'completion_time': None,
                            'error': f"HTTP {response.status}",
                            'content': None
                        }

                    resp_data = await response.json()
                    task_id = resp_data['task_id']
                    return await self.poll_result(session, task_id, start_time, file_name, test_id, duration_seconds)

        except Exception as e:
            self.metrics["failed"] += 1
            return {
                'test_id': test_id,
                'file_name': str(audio_file),
                'success': False,
                'completion_time': None,
                'error': str(e),
                'content': None
            }
        
    async def poll_result(self, session, task_id, start_time, file_name, test_id, duration_seconds):
        retries = 0
        
        while retries < self.max_retries:
            try:
                async with session.get(f"{self.base_url}/transcribe/{task_id}/result") as response:
                    if response.status != 200:
                        self.metrics["failed"] += 1
                        return {
                            'test_id': test_id,
                            'file_name': file_name,
                            'success': False,
                            'completion_time': None,
                            'duration_seconds': duration_seconds,
                            'error': f"HTTP {response.status}",
                            'content': None
                        }
                    
                    data = await response.json()
                    
                    if data['status'] == 'COMPLETED':
                        self.metrics["completed"] += 1
                        return {
                            'test_id': test_id,
                            'file_name': file_name,
                            'success': True,
                            'completion_time': time.time() - start_time,
                            'duration_seconds': duration_seconds,
                            'error': None,
                            'content': len(data['result'])
                        }
                    
                    if data['status'] == 'FAILED':
                        self.metrics["failed"] += 1
                        return {
                            'test_id': test_id,
                            'file_name': file_name,
                            'success': False,
                            'completion_time': time.time() - start_time,
                            'duration_seconds': duration_seconds,
                            'error': 'Transcription failed',
                            'content': None
                        }
                    
                    await asyncio.sleep(2)
                    retries += 1
                    
            except Exception as e:
                self.metrics["failed"] += 1
                return {
                    'test_id': test_id,
                    'file_name': file_name,
                    'success': False,
                    'completion_time': None,
                    'duration_seconds': duration_seconds,
                    'error': str(e),
                    'content': None
                }
        
        self.metrics["failed"] += 1
        return {
            'test_id': test_id,
            'file_name': file_name,
            'success': False,
            'completion_time': time.time() - start_time,
            'duration_seconds': duration_seconds,
            'error': 'Max retries exceeded',
            'content': None
        }

    async def run_load_test(self):
        audio_files = list(self.audio_files_dir.glob('*.mp3'))
        self.start_time = time.time()
        
        rate_delay = 1 / self.rate_limit  # Delay between requests based on rate limit
        
        async with aiohttp.ClientSession() as session:
            with Live(self.generate_metrics_table(), refresh_per_second=1) as live:
                
                # Background task to refresh the live metrics table periodically
                async def update_live_metrics():
                    while True:
                        live.update(self.generate_metrics_table())
                        await asyncio.sleep(1)  # Update every second
                
                metrics_task = asyncio.create_task(update_live_metrics())
                
                try:
                    tasks = set()
                    for _ in range(self.total_requests):  # Total requests
                        audio_file = random.choice(audio_files)
                        task = asyncio.create_task(self.submit_transcription(session, audio_file))
                        tasks.add(task)
                        
                        # Limit concurrent tasks
                        if len(tasks) >= self.concurrent_requests:
                            done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                            self.results.extend([t.result() for t in done])
                        
                        await asyncio.sleep(rate_delay)
                    
                    # Ensure remaining tasks are completed
                    if tasks:
                        done, _ = await asyncio.wait(tasks)
                        self.results.extend([t.result() for t in done])
                
                finally:
                    # Cancel the live metrics task when all tasks are done
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
    BASE_URL = "http://transcriber-env.eba-mdcyqpuh.us-west-2.elasticbeanstalk.com"
    AUDIO_FILES_DIR = "./audio_files"
    TOTAL_REQUESTS = 800
    CONCURRENT_REQUESTS = 800
    RATE_LIMIT = 10  # requests per second
    
    console = Console()
    load_tester = TranscriptionLoadTest(
        base_url=BASE_URL,
        total_requests=TOTAL_REQUESTS,
        audio_files_dir=AUDIO_FILES_DIR,
        concurrent_requests=CONCURRENT_REQUESTS,
        rate_limit=RATE_LIMIT
    )
    
    await load_tester.run_load_test()
    report = load_tester.generate_report()
    
    console.print("\n[bold]Test Results[/bold]")
    console.print(f"Success Rate: {report['success_rate']:.1f}%")
    console.print(f"Average Time: {report['avg_time']:.1f}s")
    console.print(f"P95 Time: {report['p95_time']:.1f}s")
    
    if report['failed_breakdown']:
        console.print("\n[bold]Errors:[/bold]")
        for error, count in report['failed_breakdown'].items():
            console.print(f"- {error}: {count}")

if __name__ == "__main__":
    asyncio.run(main())
