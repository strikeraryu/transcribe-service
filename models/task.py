from . import db
import requests
import enum

class Task(db.Model):
    class Status(enum.Enum):
        INITIALIZED = 'initialized'
        QUEUED = 'queued'
        RUNNING = 'running'
        COMPLETED = 'completed'
        FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status), default=Status.INITIALIZED)
    audio_file = db.Column(db.String(255))
    message = db.Column(db.Text)
    webhook_url = db.Column(db.Text, default="")
    payload = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    retry_count = db.Column(db.Integer, default=0)


    def trigger_webhook(self):
        try:
            if self.webhook_url and len(self.webhook_url) > 0:
                requests.get(self.webhook_url, params={"task_id": self.id, "payload": self.payload})
        except Exception as e:
            print(e)
