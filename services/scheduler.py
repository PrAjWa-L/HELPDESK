from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

scheduler = BackgroundScheduler()


def check_task_deadlines(app):
    from datetime import datetime
    from models.task import Task
    from services.email import send_deadline_email
    from extensions import db

    with app.app_context():
        now = datetime.utcnow()
        due_tasks = Task.query.filter(
            Task.deadline <= now,
            Task.deadline_email_sent == False,
            Task.status != "COMPLETED"
        ).all()

        for task in due_tasks:
            sent = send_deadline_email(task)
            if sent:
                task.deadline_email_sent = True
                db.session.commit()


def start_scheduler(app):
    scheduler.add_job(
        func=check_task_deadlines,
        args=[app],
        trigger=IntervalTrigger(minutes=1),
        id="task_deadline_check",
        replace_existing=True
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))