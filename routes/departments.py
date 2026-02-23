from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.ticket import Ticket

departments_bp = Blueprint("departments", __name__)
@departments_bp.route("/department")
@login_required
def department_view():
    if current_user.role != "ADMIN":
        return "Unauthorized", 403

    tickets = Ticket.query.filter_by(
        department=current_user.department
    ).all()

    return render_template("department.html", tickets=tickets)
