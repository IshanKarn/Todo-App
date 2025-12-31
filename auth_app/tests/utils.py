from django.db import connection
from django.test import TestCase
from auth_app.utils import hash_password

class BaseAuthTestCase(TestCase):

    def create_user(
        self,
        username="testuser",
        email="test@example.com",
        password="password123",
        verified=True,
    ):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password, is_email_verified)
                VALUES (%s, %s, %s, %s)
                """,
                [username, email, hash_password(password), verified],
            )
            return cursor.lastrowid
