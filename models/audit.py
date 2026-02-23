from datetime import datetime
from extensions import db


class TicketAudit(db.Model):
    __tablename__ = "ticket_audits"

    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    action = db.Column(db.String(50), nullable=False)  
    # CREATED / STATUS_UPDATED

    old_value = db.Column(db.String(50), nullable=True)
    new_value = db.Column(db.String(50), nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("Ticket", backref="audits")
