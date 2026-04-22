from __future__ import annotations

import pytest

from authentification.domains.login import Login


def test_login_normalizes_email() -> None:
    login = Login(email="  USER@UrbanHub.tn ", password="Password1!")
    assert login.get_email() == "user@urbanhub.tn"


@pytest.mark.parametrize(
    "email",
    ["", "   ", "invalid", "invalid@", "@invalid", "invalid.com"],
)
def test_login_rejects_invalid_email(email: str) -> None:
    with pytest.raises(ValueError):
        Login(email=email, password="Password1!")


@pytest.mark.parametrize(
    "password",
    [
        "",
        "short",
        "password1!",  # no uppercase
        "PASSWORD1!",  # no lowercase
        "Password!",  # no digit
        "Password1",  # no special
    ],
)
def test_login_rejects_invalid_password(password: str) -> None:
    with pytest.raises(ValueError):
        Login(email="user@urbanhub.tn", password=password)

