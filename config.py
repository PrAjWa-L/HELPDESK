import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(INSTANCE_DIR, "tickets.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = "uprajwal05@gmail.com"
    MAIL_PASSWORD = "jyjg iixk xntw tpmb"
    MAIL_SENDER   = "uprajwal05@gmail.com"
    MAIL_USE_TLS  = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"