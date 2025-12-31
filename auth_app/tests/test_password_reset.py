from auth_app.tests.base import RawSQLTestCase
from rest_framework.test import APITestCase

class PasswordResetTest(RawSQLTestCase, APITestCase):
    def test_forgot_password_invalid_email(self):
        res = self.client.post(
            "/api/auth/forgot-password/",
            {"email": "invalid@test.com"},
            format="json",
        )
        self.assertEqual(res.status_code, 404)
