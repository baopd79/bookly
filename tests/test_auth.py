import pytest
from fastapi import status
from src.auth.service import generate_passwd_hash, verify_password


# Test : hash password doesn't return plain text
def test_generate_passwd_hash():
    password = "Test1234"
    hashed = generate_passwd_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


# Test : verify_password returns True
def test_verify_password():
    password = "Test1234"
    hashed = generate_passwd_hash(password)
    assert verify_password(password, hashed) is True


# Test : verify_password returns False for wrong password
def test_verify_password_wrong():
    password = "Test1234"
    wrong_password = "WrongPass"
    hashed = generate_passwd_hash(password)
    assert verify_password(wrong_password, hashed) is False
