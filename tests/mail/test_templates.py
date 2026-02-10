import re

from app.auth.templates import (
    email_confirmation,
    password_reset,
    EmailTemplate,
)


def test_email_confirmation_template():
    url = "http://test.local/confirm?token=abc123"

    template = email_confirmation(url)

    assert isinstance(template, EmailTemplate)

    assert template.subject
    assert "Подтверждение" in template.subject

    assert template.html
    assert template.text

    assert url in template.html
    assert url in template.text


def test_password_reset_template():
    url = "http://test.local/reset?token=xyz987"

    template = password_reset(url)

    assert isinstance(template, EmailTemplate)

    assert "Сброс" in template.subject

    assert url in template.html
    assert url in template.text


def test_templates_do_not_contain_unrendered_placeholders():
    url = "http://example.com"

    template = email_confirmation(url)

    # чтобы случайно не забыть f-string
    assert "{confirm_url}" not in template.html
    assert "{confirm_url}" not in template.text


def test_html_contains_link():
    url = "http://example.com"

    template = email_confirmation(url)

    assert re.search(r'<a\s+href="http://example.com"', template.html)
