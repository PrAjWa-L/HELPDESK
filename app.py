from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager
from models.user import User
from models.comment import TicketComment
from flask_login import login_required
from routes import auth_bp, tickets_bp, departments_bp, reports_bp, dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(dashboard_bp)

    # Index route
    @app.route("/")
    @login_required
    def index():
        return redirect(url_for("dashboard.dashboard"))

    # Seed admin accounts safely
    with app.app_context():
        db.create_all()
        seed_admins()

    return app


def seed_admins():
    from models.user import User

    # Create SUPER_ADMIN if missing
    if not User.query.filter_by(role="SUPER_ADMIN").first():
        super_admin = User(
            username="superadmin",
            role="SUPER_ADMIN",
            department=None
        )
        super_admin.set_password("super123")
        db.session.add(super_admin)

    # Fixed department admins
    fixed_admins = [
        ("itadmin", "IT"),
        ("hradmin", "HR"),
        ("maintadmin", "MAINTENANCE"),
    ]

    for username, dept in fixed_admins:
        existing = User.query.filter_by(username=username).first()
        if not existing:
            admin = User(
                username=username,
                role="ADMIN",
                department=dept
            )
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
