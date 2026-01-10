#!/usr/bin/env python3
"""Generate password hash for initial users."""

import bcrypt

def hash_password(password: str) -> str:
    """Generate bcrypt hash for password."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# Generate hashes for common passwords
passwords = {
    'admin1234': '관리자',
    'expert1234': '전문가',
    'applicant1234': '지원자'
}

print("Password hashes:")
for password, description in passwords.items():
    hashed = hash_password(password)
    print(f"'{password}': '{hashed}'  -- {description}")