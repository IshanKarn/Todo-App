from django.db import connection
from auth_app.utils import hash_password

from auth_app.tests.base import RawSQLTestCase
from rest_framework.test import APITestCase

class DeleteUserTest(RawSQLTestCase, APITestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password, is_email_verified)
                VALUES (%s, %s, %s, 1)
                """,
                ["test", "test@test.com", hash_password("password123")],
            )
            self.user_id = cursor.lastrowid

    def test_delete_user_unauthorized(self):
        res = self.client.delete("/api/auth/delete-user/")
        self.assertEqual(res.status_code, 403)
