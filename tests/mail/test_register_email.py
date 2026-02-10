from unittest.mock import patch


def test_register_sends_confirmation_email(
    client,
    db_session,
):
    payload = {
        "email": "newuser@test.com",
        "password": "StrongPassword123!",
        "password_confirm": "StrongPassword123!",
    }

    with patch(
        "app.auth.service.send_email_confirmation"
    ) as mock_send_email:

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 201

        mock_send_email.assert_called_once()

        args, kwargs = mock_send_email.call_args
        assert args[0] == payload["email"]
        assert "confirm-email" in args[1]
