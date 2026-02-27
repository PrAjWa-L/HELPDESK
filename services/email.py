import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def send_deadline_email(task):
    try:
        mail_server   = current_app.config.get("MAIL_SERVER", "")
        mail_port     = int(current_app.config.get("MAIL_PORT", 587))
        mail_username = current_app.config.get("MAIL_USERNAME", "")
        mail_password = current_app.config.get("MAIL_PASSWORD", "")
        mail_sender   = current_app.config.get("MAIL_SENDER", mail_username)
        use_tls       = current_app.config.get("MAIL_USE_TLS", True)

        if not mail_server or not mail_username:
            current_app.logger.warning("Email not configured — skipping deadline email.")
            return False

        # Fetch recipients: MAINTENANCE admin + SUPER_ADMIN
        from models.user import User
        recipients = User.query.filter(
            User.email.isnot(None),
            User.email != "",
            ((User.role == "ADMIN") & (User.department == "MAINTENANCE")) |
            (User.role == "SUPER_ADMIN")
        ).all()

        to_addresses = [u.email for u in recipients]

        if not to_addresses:
            current_app.logger.warning(f"No recipient emails found for task #{task.id} — skipping.")
            return False

        subject = f"[Helpdesk] Task Deadline Reached: {task.title}"

        body = f"""
Hello,

This is an automated reminder from the CUTIS Helpdesk system.

The following maintenance task has reached its deadline:

  Task        : {task.title}
  Description : {task.description or '—'}
  Assigned To : {task.assigned_to}
  Deadline    : {task.deadline.strftime('%d %b %Y at %I:%M %p')}
  Status      : {task.status}

Please log in to the Helpdesk to review and update this task.

— CUTIS Internal Helpdesk
        """.strip()

        msg = MIMEMultipart()
        msg["From"]    = mail_sender
        msg["To"]      = ", ".join(to_addresses)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(mail_server, mail_port) as server:
            if use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(mail_sender, to_addresses, msg.as_string())

        current_app.logger.info(f"Deadline email sent for task #{task.id} to {to_addresses}")
        return True

    except Exception as e:
        current_app.logger.error(f"Failed to send deadline email for task #{task.id}: {e}")
        return False