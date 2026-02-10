# app/tasks/email_tasks.py
from celery import shared_task
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.settings import settings
from app.auth.templates import email_confirmation, password_reset


@shared_task(name='send_email_confirmation', bind=True, max_retries=3)
def send_email_confirmation(self, to_email: str, token: str):
    """
    Отправка письма для подтверждения регистрации
    """
    try:
        template = email_confirmation(confirm_url)

        _email(
            to_email=to_email,
            subject=template.subject,
            html_body=template.html,
            text_body=template.text,
        )

        return {"status": "success", "email": to_email, "type": "confirmation"}

    except Exception as exc:
        # Повторная попытка при ошибке
        raise self.retry(exc=exc, countdown=60)  # Повтор через 60 секунд


@shared_task(name='send_password_reset', bind=True, max_retries=3)
def send_password_reset(self, to_email: str, token: str):
    """
    Отправка письма для сброса пароля
    """
    try:
        template = password_reset(reset_url)

        _email(
            to_email=to_email,
            subject=template.subject,
            html_body=template.html,
            text_body=template.text,
        )

        return {"status": "success", "email": to_email, "type": "password_reset"}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


def _email(
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
):
    """
    Внутренняя функция для отправки письма через SMTP
    """

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD: # Консольный режим для тестирования
        print(f"\n{'=' * 60}")
        print(f"📧 EMAIL PREVIEW (Console Mode)")
        print(f"{'=' * 60}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"\n{text_body}")
        print(f"{'=' * 60}\n")
        return

    try:
        # Создаём сообщение
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_FROM or 'noreply@todolist.com'
        msg['To'] = to_email

        # Текстовая версия
        part1 = MIMEText(text_body, 'plain')
        # HTML версия
        part2 = MIMEText(html_body, 'html')

        msg.attach(part1)
        msg.attach(part2)

        # Подключаемся к SMTP серверу
        if settings.EMAIL_USE_TLS:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)

        # Авторизация
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        # Отправка
        server.send_message(msg)
        server.quit()

        print(f"[EMAIL SENT] To: {to_email}, Subject: {subject}")

    except Exception as e:
        print(f"[EMAIL ERROR] To: {to_email}, Error: {str(e)}")
        raise


