import os
import unittest
from unittest.mock import patch

from src.auth import authenticate, get_auth_users


class AuthTests(unittest.TestCase):
    def test_auth_with_json_users(self):
        fake_users = '[{"email":"admin@smartcafe.local","password":"secret","name":"Admin","role":"admin"}]'
        with patch.dict(os.environ, {"SMARTCAFE_AUTH_USERS_JSON": fake_users}, clear=False):
            users = get_auth_users()
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0]["email"], "admin@smartcafe.local")
            self.assertIsNotNone(authenticate("admin@smartcafe.local", "secret"))

    def test_auth_fallback_env_admin(self):
        env = {
            "SMARTCAFE_AUTH_USERS_JSON": "",
            "SMARTCAFE_ADMIN_EMAIL": "owner@smartcafe.local",
            "SMARTCAFE_ADMIN_PASSWORD": "owner-pass",
        }
        with patch.dict(os.environ, env, clear=False):
            user = authenticate("owner@smartcafe.local", "owner-pass")
            self.assertIsNotNone(user)
            self.assertEqual(user["email"], "owner@smartcafe.local")


if __name__ == "__main__":
    unittest.main()
