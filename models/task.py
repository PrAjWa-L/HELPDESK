from datetime import datetime
from extensions import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    assigned_to = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(30), nullable=False, default="PENDING")
    # PENDING / IN_PROGRESS / COMPLETED

   
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    deadline_email_sent = db.Column(db.Boolean, default=False, nullable=False)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_by = db.relationship("User", backref="tasks")