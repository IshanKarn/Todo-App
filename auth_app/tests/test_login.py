from django.db import connection
from auth_app.utils import hash_password

from auth_app.tests.base import RawSQLTestCase
from rest_framework.test import APITestCase

class LoginAPITest(RawSQLTestCase, APITestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password, is_email_verified)
                VALUES (%s, %s, %s, 1)
                """,
                ["test", "test@test.com", hash_password("password123")],
            )

    def test_login_success(self):
        res = self.client.post(
            "/api/auth/login/",
            {
                "username_or_email": "test",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
