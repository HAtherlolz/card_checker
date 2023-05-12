from pathlib import Path

from config.conf import settings

from app.services.email.send_email import send_email


def send_password_email(email_to: str, token: str) -> None:
    """
        Send email for reset password
    """
    project_name = settings.EMAILS_FROM_NAME
    subject = f"{project_name} - Reset password email"
    with open(Path(__file__).parent.parent.parent / 'templates' / "reset_password.html") as f:
        template_str = f.read()
    print(email_to)
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "protocol": "https",
            "domain": settings.DOMAIN,
            "url": token
        }
    )
