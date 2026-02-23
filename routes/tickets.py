from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.ticket import Ticket
from models.audit import TicketAudit
from models.comment import TicketComment
from services.sla import calculate_sla_due_at
from datetime import datetime

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/tickets/create", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        issue_type = request.form["issue_type"]
        department = request.form["department"]
        other_note = request.form.get("other_department", "").strip() if department == "OTHER" else None
        location = request.form["location"]
        priority = request.form["priority"]

        ticket = Ticket(
            title=title,
            description=description,
            issue_type=issue_type,
            department=department,
            other_department_note=other_note,
            location=location,
            priority=priority,
            status="OPEN",
            created_by=current_user
        )

        ticket.sla_due_at = calculate_sla_due_at(priority)

        db.session.add(ticket)
        db.session.flush()

        audit = TicketAudit(
            ticket_id=ticket.id,
            action="CREATED"
        )
        db.session.add(audit)
        db.session.commit()

        flash("Ticket submitted successfully.", "success")
        return redirect(url_for("index"))

    return render_template("create_ticket.html")


@tickets_bp.route("/tickets")
@login_required
def list_tickets():
    if current_user.role == "USER":
        tickets = Ticket.query.filter_by(created_by_id=current_user.id).all()

    elif current_user.role == "ADMIN":
        # Admins see their own dept tickets + all OTHER tickets
        tickets = Ticket.query.filter(
            db.or_(
                Ticket.department == current_user.department,
                Ticket.department == "OTHER"
            )
        ).all()

    elif current_user.role == "SUPER_ADMIN":
        tickets = Ticket.query.all()

    else:
        tickets = []

    return render_template("tickets_list.html", tickets=tickets, now=datetime.utcnow())


@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role == "USER":
        if ticket.created_by_id != current_user.id:
            return "Unauthorized", 403

    elif current_user.role == "ADMIN":
        # Admins can access their own dept + OTHER tickets
        if ticket.department != current_user.department and ticket.department != "OTHER":
            return "Unauthorized", 403

    # SUPER_ADMIN can view any ticket
    return render_template("ticket_detail.html", ticket=ticket, now=datetime.utcnow())


@tickets_bp.route("/tickets/<int:ticket_id>/update_status", methods=["POST"])
@login_required
def update_status(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role not in ("ADMIN", "SUPER_ADMIN"):
        return "Unauthorized", 403

    if current_user.role == "ADMIN" and ticket.department != current_user.department and ticket.department != "OTHER":
        return "Unauthorized", 403

    new_status = request.form["status"]
    old_status = ticket.status

    if new_status not in ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]:
        flash("Invalid status.", "danger")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    ticket.status = new_status

    if new_status == "CLOSED":
        ticket.closed_at = datetime.utcnow()

    # If moving away from RESOLVED, clear acknowledgment
    if old_status == "RESOLVED" and new_status != "RESOLVED":
        ticket.acknowledged_at = None

    audit = TicketAudit(
        ticket_id=ticket.id,
        action="STATUS_UPDATED",
        old_value=old_status,
        new_value=new_status
    )
    db.session.add(audit)
    db.session.commit()

    flash(f"Status updated to {new_status}.", "success")
    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))


@tickets_bp.route("/tickets/<int:ticket_id>/comment", methods=["POST"])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role != "SUPER_ADMIN":
        return "Unauthorized", 403

    body = request.form.get("body", "").strip()
    if not body:
        flash("Comment cannot be empty.", "warning")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    comment = TicketComment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        body=body
    )
    db.session.add(comment)

    audit = TicketAudit(
        ticket_id=ticket.id,
        action="COMMENT_ADDED"
    )
    db.session.add(audit)
    db.session.commit()

    flash("Comment added.", "success")
    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))


@tickets_bp.route("/tickets/<int:ticket_id>/acknowledge", methods=["POST"])
@login_required
def acknowledge_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.role != "USER" or ticket.created_by_id != current_user.id:
        return "Unauthorized", 403

    if ticket.status != "RESOLVED":
        flash("You can only acknowledge a resolved ticket.", "warning")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    if ticket.acknowledged_at:
        flash("Ticket already acknowledged.", "info")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    ticket.acknowledged_at = datetime.utcnow()

    audit = TicketAudit(
        ticket_id=ticket.id,
        action="ACKNOWLEDGED"
    )
    db.session.add(audit)
    db.session.commit()

    flash("Thank you for acknowledging the resolution!", "success")
    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))
