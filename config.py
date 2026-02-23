import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Ensure the instance folder exists before SQLite tries to open it
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = "dev-secret-key"  # will be replaced in prod
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + os.path.join(INSTANCE_DIR, "tickets.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
