from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.ticket import Ticket
from models.audit import TicketAudit
from models.task import Task
from extensions import db
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    now = datetime.utcnow()

    if current_user.role == "SUPER_ADMIN":
        base_query = Ticket.query

    elif current_user.role == "ADMIN":
        base_query = Ticket.query.filter(
            db.or_(
                Ticket.department == current_user.department,
                Ticket.department == "OTHER"
            )
        )

    elif current_user.role == "USER":
        base_query = Ticket.query.filter_by(created_by_id=current_user.id)

    else:
        base_query = Ticket.query.filter_by(id=None)

    tickets = base_query.all()

    total_tickets = len(tickets)
    open_tickets  = len([t for t in tickets if t.status == "OPEN"])
    in_progress   = len([t for t in tickets if t.status == "IN_PROGRESS"])
    resolved      = len([t for t in tickets if t.status == "RESOLVED"])
    closed        = len([t for t in tickets if t.status == "CLOSED"])

    overdue = len([
        t for t in tickets
        if t.sla_due_at and t.sla_due_at < now and t.status not in ("CLOSED", "RESOLVED")
    ])

    priority_counts = {
        "DESIRABLE": len([t for t in tickets if t.priority == "DESIRABLE"]),
        "ESSENTIAL": len([t for t in tickets if t.priority == "ESSENTIAL"]),
        "CRITICAL":  len([t for t in tickets if t.priority == "CRITICAL"]),
    }

    if current_user.role == "SUPER_ADMIN":
        recent_activity = TicketAudit.query.order_by(
            TicketAudit.timestamp.desc()
        ).limit(10).all()

    elif current_user.role == "ADMIN":
        recent_activity = (
            TicketAudit.query
            .join(Ticket)
            .filter(
                db.or_(
                    Ticket.department == current_user.department,
                    Ticket.department == "OTHER"
                )
            )
            .order_by(TicketAudit.timestamp.desc())
            .limit(10)
            .all()
        )

    else:
        ticket_ids = [t.id for t in tickets]
        if ticket_ids:
            recent_activity = (
                TicketAudit.query
                .filter(TicketAudit.ticket_id.in_(ticket_ids))
                .order_by(TicketAudit.timestamp.desc())
                .limit(10)
                .all()
            )
        else:
            recent_activity = []

    department_counts = None
    if current_user.role == "SUPER_ADMIN":
        department_counts = {
            "IT":          len([t for t in tickets if t.department == "IT"]),
            "HR":          len([t for t in tickets if t.department == "HR"]),
            "MAINTENANCE": len([t for t in tickets if t.department == "MAINTENANCE"]),
            "OTHER":       len([t for t in tickets if t.department == "OTHER"]),
        }

    # ── Task summary for MAINTENANCE admin and SUPER_ADMIN ──
    tasks_summary = None
    if current_user.role == "SUPER_ADMIN" or (
        current_user.role == "ADMIN" and current_user.department == "MAINTENANCE"
    ):
        all_tasks = Task.query.all()
        tasks_summary = {
            "total":     len(all_tasks),
            "pending":   len([t for t in all_tasks if t.status == "PENDING"]),
            "in_progress": len([t for t in all_tasks if t.status == "IN_PROGRESS"]),
            "completed": len([t for t in all_tasks if t.status == "COMPLETED"]),
            "overdue":   len([
                t for t in all_tasks
                if t.deadline < now and t.status != "COMPLETED"
            ]),
            "upcoming":  Task.query.filter(
                Task.deadline > now,
                Task.status != "COMPLETED"
            ).order_by(Task.deadline.asc()).limit(5).all()
        }

    return render_template(
        "dashboard.html",
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        in_progress=in_progress,
        resolved=resolved,
        closed=closed,
        overdue=overdue,
        priority_counts=priority_counts,
        recent_activity=recent_activity,
        department_counts=department_counts,
        tasks_summary=tasks_summary,
        now=now,
    )