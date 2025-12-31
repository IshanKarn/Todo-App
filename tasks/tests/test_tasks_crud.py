from django.db import connection
from auth_app.utils import hash_password, create_access_token

from auth_app.tests.base import RawSQLTestCase
from rest_framework.test import APITestCase

class TaskAPITest(RawSQLTestCase, APITestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password, is_email_verified)
                VALUES (%s, %s, %s, 1)
                """,
                ["taskuser", "task@test.com", hash_password("password123")],
            )
            self.user_id = cursor.lastrowid

        self.token = create_access_token(self.user_id)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )

    def test_create_task(self):
        res = self.client.post(
            "/api/tasks/",
            {"title": "Test Task"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)

    def test_get_tasks(self):
        res = self.client.get("/api/tasks/")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.data, list)
