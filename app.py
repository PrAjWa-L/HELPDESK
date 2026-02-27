from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager
from models.user import User
from models.task import Task
from models.comment import TicketComment
from flask_login import login_required
from routes import auth_bp, tickets_bp, departments_bp, reports_bp, dashboard_bp, tasks_bp
from datetime import timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    IST = timezone(timedelta(hours=5, minutes=30))

    @app.template_filter('ist')
    def ist_filter(dt):
        if dt is None:
            return '—'
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime('%d %b %Y, %I:%M %p')
    
    @app.template_filter('ist_input')
    def ist_input_filter(dt):
        if dt is None:
            return ''
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime('%Y-%m-%dT%H:%M')
    
    @app.template_filter('ist_short')
    def ist_short_filter(dt):
        if dt is None:
            return '—'
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime('%d %b, %I:%M %p')

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)

    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("dashboard.dashboard"))

    with app.app_context():
        db.create_all()
        seed_admins()

    import os
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from services.scheduler import start_scheduler
        start_scheduler(app)

    return app


def seed_admins():
    from models.user import User

    if not User.query.filter_by(role="SUPER_ADMIN").first():
        super_admin = User(
            username="superadmin",
            role="SUPER_ADMIN",
            department=None,
            email="prajwaludupa6@gmail.com"        # ← set real COO email here
        )
        super_admin.set_password("super123")
        db.session.add(super_admin)

    for username, dept, email in [
        ("itadmin",   "IT",          "it@cutis.org"),
        ("hradmin",   "HR",          "hr@cutis.org"),
        ("maintadmin","MAINTENANCE", "iamvenom2004@gmail.com"),  # ← set real email
    ]:
        if not User.query.filter_by(username=username).first():
            admin = User(username=username, role="ADMIN", department=dept, email=email)
            admin.set_password("admin123")
            db.session.add(admin)

    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.login_view = "auth.login"


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)