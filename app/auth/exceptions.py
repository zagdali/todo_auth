# app/auth/exceptions.py
class AuthError(Exception):
    message = "Ошибка авторизации"


class InvalidCredentials(AuthError):
    message = "Проверьте корректность введенных данных"


class EmailAlreadyExists(AuthError):
    message = "Проверьте корректность введенных данных"


class EmailNotVerified(AuthError):
    message = "Подтвердите email для входа"

class ValidationError(Exception):
    def __init__(self, code: str, message: str, field: str):
        self.code = code
        self.message = message
        self.field = field