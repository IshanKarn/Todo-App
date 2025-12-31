from django.db import connection

from auth_app.tests.base import RawSQLTestCase
from rest_framework.test import APITestCase

class VerifyEmailOTPTest(RawSQLTestCase, APITestCase):
    def test_invalid_otp(self):
        res = self.client.post(
            "/api/auth/verify-email/",
            {
                "email": "fake@test.com",
                "otp": "000000",
            },
            format="json",
        )

        self.assertEqual(res.status_code, 400)
