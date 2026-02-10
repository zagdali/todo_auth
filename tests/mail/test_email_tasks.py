from unittest.mock import patch

from app.tasks.email_tasks import send_email_confirmation


@patch("app.tasks.email_tasks._email")
def test_send_email_confirmation_calls_email(mock_email):
    to_email = "user@test.com"
    url = "http://test.local/confirm?token=123"

    send_email_confirmation(to_email, url)

    mock_email.assert_called_once()

    args, kwargs = mock_email.call_args

    assert kwargs["to_email"] == to_email
    assert url in kwargs["html_body"]
    assert url in kwargs["text_body"]
    assert kwargs["subject"]

@patch("app.tasks.email_tasks._email")
def test_send_password_reset_email(mock_email):
    from app.tasks.email_tasks import send_password_reset_email

    to_email = "user@test.com"
    url = "http://test.local/reset?token=456"

    send_password_reset_email(to_email, url)

    mock_email.assert_called_once()

    _, kwargs = mock_email.call_args

    assert kwargs["to_email"] == to_email
    assert url in kwargs["html_body"]
