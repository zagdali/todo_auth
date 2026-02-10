# app/auth/templates.py

from dataclasses import dataclass


@dataclass(slots=True)
class EmailTemplate:
    subject: str
    html: str
    text: str


def email_confirmation(confirm_url: str) -> EmailTemplate:
    subject = "Подтверждение регистрации в TODOLIST"

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #333;">Добро пожаловать в TODOLIST!</h2>
            <p>Спасибо за регистрацию. Пожалуйста, подтвердите вашу почту:</p>

            <div style="margin: 20px 0;">
                <a href="{confirm_url}"
                   style="
                       display: inline-block;
                       padding: 12px 24px;
                       background-color: #007bff;
                       color: white;
                       text-decoration: none;
                       border-radius: 5px;
                   ">
                    Подтвердить почту
                </a>
            </div>

            <p>Или скопируйте ссылку в браузер:</p>
            <p style="word-break: break-all;">{confirm_url}</p>

            <p style="color: #888; font-size: 12px;">
                Ссылка действительна в течение 24 часов.
            </p>
        </body>
    </html>
    """

    text = f"""
    Добро пожаловать в TODOLIST!

    Спасибо за регистрацию.
    Подтвердите почту по ссылке:

    {confirm_url}

    Ссылка действительна 24 часа.
    """

    return EmailTemplate(subject, html, text)


def password_reset(reset_url: str) -> EmailTemplate:
    subject = "Сброс пароля в TODOLIST"

    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>Запрос на сброс пароля</h2>
            <p>Вы запросили сброс пароля.</p>
            <p>Если это были не вы — просто проигнорируйте письмо.</p>

            <div style="margin: 20px 0;">
                <a href="{reset_url}"
                   style="
                       display: inline-block;
                       padding: 12px 24px;
                       background-color: #dc3545;
                       color: white;
                       text-decoration: none;
                       border-radius: 5px;
                   ">
                    Сбросить пароль
                </a>
            </div>

            <p>Или скопируйте ссылку:</p>
            <p style="word-break: break-all;">{reset_url}</p>

            <p style="color: #888; font-size: 12px;">
                Ссылка действительна 1 час.
            </p>
        </body>
    </html>
    """

    text = f"""
    Запрос на сброс пароля

    Если это были не вы — проигнорируйте письмо.

    Ссылка:
    {reset_url}

    Срок действия — 1 час.
    """

    return EmailTemplate(subject, html, text)
