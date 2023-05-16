from pathlib import Path

from config.conf import settings

from app.services.email.send_email import send_email


def send_excel_email(email_to: str, file) -> None:
    """
        Send email for reset password
    """
    project_name = settings.EMAILS_FROM_NAME
    subject = f"{project_name} - Analiz of credit card"
    with open(Path(__file__).parent.parent.parent / 'templates' / "excel_analiz.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        file=file
    )
