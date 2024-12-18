from . import db
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
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    retry_count = db.Column(db.Integer, default=0)
