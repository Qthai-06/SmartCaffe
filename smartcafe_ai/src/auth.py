import json
import os
from typing import Dict, List, Optional


def _default_users() -> List[Dict[str, str]]:
    email = os.getenv("SMARTCAFE_ADMIN_EMAIL", "").strip()
    password = os.getenv("SMARTCAFE_ADMIN_PASSWORD", "").strip()
    name = os.getenv("SMARTCAFE_ADMIN_NAME", "Admin").strip() or "Admin"
    role = os.getenv("SMARTCAFE_ADMIN_ROLE", "admin").strip() or "admin"

    if not email or not password:
        return []

    return [{"email": email, "password": password, "name": name, "role": role}]


def get_auth_users() -> List[Dict[str, str]]:
    raw = os.getenv("SMARTCAFE_AUTH_USERS_JSON", "").strip()
    if not raw:
        return _default_users()

    try:
        users = json.loads(raw)
    except json.JSONDecodeError:
        return _default_users()

    normalized: List[Dict[str, str]] = []
    if not isinstance(users, list):
        return _default_users()

    for user in users:
        if not isinstance(user, dict):
            continue
        email = str(user.get("email", "")).strip()
        password = str(user.get("password", "")).strip()
        if not email or not password:
            continue
        normalized.append(
            {
                "email": email,
                "password": password,
                "name": str(user.get("name", "Admin")).strip() or "Admin",
                "role": str(user.get("role", "staff")).strip() or "staff",
            }
        )

    return normalized or _default_users()


def authenticate(email: str, password: str) -> Optional[Dict[str, str]]:
    email = (email or "").strip()
    password = (password or "").strip()

    for user in get_auth_users():
        if user["email"] == email and user["password"] == password:
            return user
    return None

