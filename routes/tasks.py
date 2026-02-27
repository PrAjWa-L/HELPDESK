from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.task import Task
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)


def _maintenance_admin_required():
    return current_user.role == "ADMIN" and current_user.department == "MAINTENANCE"


def _can_view_tasks():
    return current_user.role == "SUPER_ADMIN" or _maintenance_admin_required()


@tasks_bp.route("/tasks")
@login_required
def task_list():
    if not _can_view_tasks():
        return "Unauthorized", 403

    now = datetime.utcnow()
    tasks = Task.query.order_by(Task.deadline.asc()).all()
    return render_template("tasks.html", tasks=tasks, now=now)


@tasks_bp.route("/tasks/create", methods=["GET", "POST"])
@login_required
def create_task():
    if not _maintenance_admin_required():
        return "Unauthorized", 403

    if request.method == "POST":
        title        = request.form["title"].strip()
        description  = request.form.get("description", "").strip()
        assigned_to  = request.form["assigned_to"].strip()
        deadline_str = request.form["deadline"]
        status       = request.form.get("status", "PENDING")

        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid deadline format.", "danger")
            return redirect(url_for("tasks.create_task"))

        task = Task(
            title=title,
            description=description,
            assigned_to=assigned_to,
            deadline=deadline,
            status=status,
            created_by_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()

        flash("Task created successfully.", "success")
        return redirect(url_for("tasks.task_list"))

    return render_template("task_form.html", task=None, action="Create")


@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    if not _maintenance_admin_required():
        return "Unauthorized", 403

    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        task.title        = request.form["title"].strip()
        task.description  = request.form.get("description", "").strip()
        task.assigned_to  = request.form["assigned_to"].strip()
        task.status       = request.form.get("status", task.status)

        deadline_str = request.form["deadline"]
        try:
            new_deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid deadline format.", "danger")
            return redirect(url_for("tasks.edit_task", task_id=task_id))

        # If deadline changed, reset email flag so a fresh ping fires
        if new_deadline != task.deadline:
            task.deadline = new_deadline
            task.deadline_email_sent = False

        db.session.commit()
        flash("Task updated.", "success")
        return redirect(url_for("tasks.task_list"))

    return render_template("task_form.html", task=task, action="Edit")


@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    if not _maintenance_admin_required():
        return "Unauthorized", 403

    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "success")
    return redirect(url_for("tasks.task_list"))