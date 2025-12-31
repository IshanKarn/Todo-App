from django.urls import reverse

from auth_app.tests.base import RawSQLTestCase
from rest_framework.test import APITestCase

class RegisterAPITest(RawSQLTestCase, APITestCase):
    def test_register_new_user(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["action"], "verify_email")

    def test_register_existing_email(self):
        self.client.post(
            "/api/auth/register/",
            {
                "username": "user1",
                "email": "user@test.com",
                "password": "password123",
            },
            format="json",
        )

        res = self.client.post(
            "/api/auth/register/",
            {
                "username": "user2",
                "email": "user@test.com",
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(res.message, "Email already registered but not verified")
