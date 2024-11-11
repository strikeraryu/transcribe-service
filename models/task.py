from . import db
import enum

class Task(db.Model):
    class ActionType(enum.Enum):
        TRANSCRIBE = "transcribe"

    class Status(enum.Enum):
        QUEUED = 'queued'
        RUNNING = 'running'
        COMPLETED = 'completed'
        FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum(Status), default=Status.QUEUED)
    action_type = db.Column(db.Enum(ActionType), default=ActionType.TRANSCRIBE)
    result = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    retry_count = db.Column(db.Integer, default=0)
