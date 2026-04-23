from __future__ import annotations

from authentification.security.password_hasher import BcryptPasswordHasher


def test_hash_and_verify_password() -> None:
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash_password("Password1!")

    assert isinstance(hashed, str)
    assert hashed != "Password1!"
    assert hasher.verify_password("Password1!", hashed) is True
    assert hasher.verify_password("WrongPassword1!", hashed) is False

