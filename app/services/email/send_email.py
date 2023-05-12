import emails

from emails.template import JinjaTemplate

from config.conf import settings


def send_email(email_to: str, subject_template="", html_template="", environment={}):
    """ Email sending """
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.MAIL_FROM),
    )
    smtp_options = {"host": settings.MAIL_SERVER, "port": settings.MAIL_PORT}
    if settings.MAIL_SSL_TLS:
        smtp_options["tls"] = settings.MAIL_SSL_TLS
    if settings.MAIL_USERNAME:
        smtp_options["user"] = settings.MAIL_USERNAME
    if settings.MAIL_PASSWORD:
        smtp_options["password"] = settings.MAIL_PASSWORD
    message.send(to=email_to, render=environment, smtp=smtp_options)
