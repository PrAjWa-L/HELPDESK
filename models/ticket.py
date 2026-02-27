from datetime import datetime
from extensions import db


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    raiser_name = db.Column(db.String(100), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    issue_type = db.Column(db.String(100), nullable=False)

    department = db.Column(db.String(50), nullable=False)
    other_department_note = db.Column(db.String(200), nullable=True)  # filled when department = OTHER
    location = db.Column(db.String(100), nullable=False)

    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="OPEN")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sla_due_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)  # set when user acknowledges resolution

    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_by = db.relationship("User", backref="tickets")
