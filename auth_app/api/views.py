from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection,transaction

from auth_app.api.permissions import IsJWTAuthenticated
from auth_app.authentication import JWTAuthentication

import random
from datetime import datetime, timedelta
from django.core.mail import send_mail

from auth_app.utils import (
    create_access_token, create_refresh_token,
    verify_password, hash_password,
    is_valid_email
)


class RegisterAPI(APIView):

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response({"error": "All fields required"}, status=400)
        
        if not is_valid_email(email):
            return Response({"error": "Invalid email format"}, status=400)

        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
                """,
                [username, email, hash_password(password)],
            )

            user_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO password_otps (user_id, otp, expires_at)
                VALUES (%s, %s, %s)
                """,
                [user_id, otp, expiry],
            )

        send_mail(
            "Verify your email",
            f"Your verification OTP is {otp}. Valid for 5 minutes.",
            None,
            [email],
        )

        return Response({"message": "OTP sent to email"})

class VerifyEmailOTP(APIView):

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT o.id, u.id
                FROM password_otps o
                JOIN users u ON u.id = o.user_id
                WHERE u.email=%s AND o.otp=%s
                  AND o.is_used=0 AND o.expires_at > CURRENT_TIMESTAMP
            """, [email, otp])

            row = cursor.fetchone()

            if not row:
                return Response({"error": "Invalid or expired OTP"}, status=400)

            otp_id, user_id = row

            cursor.execute(
                "UPDATE password_otps SET is_used=1 WHERE id=%s",
                [otp_id],
            )
            cursor.execute(
                "UPDATE users SET is_email_verified=1 WHERE id=%s",
                [user_id],
            )

        return Response({"message": "Email verified"})


class LoginAPI(APIView):

    def post(self, request):
        username_or_email = request.data.get("username_or_email")
        password = request.data.get("password")

        if not username_or_email or not password:
            return Response(
                {"error": "username/email and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, password, email, is_email_verified
                FROM users
                WHERE (username = %s OR email = %s) AND is_active = 1
                """,
                [username_or_email, username_or_email],
            )
            user = cursor.fetchone()

        # User not found
        if not user:
            # auth_logger.warning(f"LOGIN_FAILED | username={username}")
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id, hashed_password, email, is_email_verified = user

        # Password incorrect
        if not verify_password(password, hashed_password):
            # auth_logger.warning(
            #     f"LOGIN_FAILED | user_id={user_id} reason=wrong_password"
            # )
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Email NOT verified → resend OTP
        if not is_email_verified:
            otp = str(random.randint(100000, 999999))
            expiry = datetime.utcnow() + timedelta(minutes=5)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO password_otps (user_id, otp, expires_at)
                    VALUES (%s, %s, %s)
                    """,
                    [user_id, otp, expiry],
                )

            send_mail(
                subject="Verify your email",
                message=f"Your email verification OTP is {otp}. Valid for 5 minutes.",
                from_email=None,
                recipient_list=[email],
            )

            # auth_logger.info(
            #     f"LOGIN_BLOCKED_EMAIL_NOT_VERIFIED | user_id={user_id}"
            # )

            return Response(
                {
                    "error": "Email not verified",
                    "message": "Verification OTP sent to your email",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Email verified → proceed with login
        access = create_access_token(user_id)
        refresh = create_refresh_token(user_id)

        # auth_logger.info(
        #     f"LOGIN_SUCCESS | user_id={user_id}"
        # )

        return Response(
            {
                "access": access,
                "refresh": refresh,
            },
            status=status.HTTP_200_OK,
        )

class LogoutAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    def post(self, request):
        """
        Stateless logout.
        Client must delete JWT.
        """
        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )

class PasswordResetAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    def put(self, request):
        user_id = request.user["user_id"]
        new_password = request.data.get("password")

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password=%s WHERE id=%s",
                [hash_password(new_password), user_id],
            )

        return Response({"message": "Password updated"})
    
class ForgotPasswordAPI(APIView):

    def post(self, request):
        email = request.data.get("email")

        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email=%s AND is_email_verified=1",
                [email],
            )
            user = cursor.fetchone()

            if not user:
                return Response({"error": "Email not registered"}, status=404)

            cursor.execute(
                """
                INSERT INTO password_otps (user_id, otp, expires_at)
                VALUES (%s, %s, %s)
                """,
                [user[0], otp, expiry],
            )

        send_mail(
            "Password reset OTP",
            f"Your password reset OTP is {otp}. Valid for 5 minutes.",
            None,
            [email],
        )

        return Response({"message": "OTP sent"})

class ResetPasswordOTP(APIView):

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT o.id, u.id
                FROM password_otps o
                JOIN users u ON u.id=o.user_id
                WHERE u.email=%s AND o.otp=%s
                  AND o.is_used=0 AND o.expires_at > CURRENT_TIMESTAMP
            """, [email, otp])

            row = cursor.fetchone()
            if not row:
                return Response({"error": "Invalid or expired OTP"}, status=400)

            otp_id, user_id = row

            cursor.execute(
                "UPDATE users SET password=%s WHERE id=%s",
                [hash_password(new_password), user_id],
            )
            cursor.execute(
                "UPDATE password_otps SET is_used=1 WHERE id=%s",
                [otp_id],
            )

        return Response({"message": "Password reset successful"})


class DeleteUserCascadeAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    def delete(self, request):
        user_id = request.user["user_id"]

        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # 1️⃣ Delete tasks first
                    cursor.execute(
                        "DELETE FROM tasks WHERE user_id = %s",
                        [user_id],
                    )

                    # 2️⃣ Delete password otps
                    cursor.execute(
                        "DELETE FROM password_otps  WHERE user_id = %s",
                        [user_id],
                    )

                    # 2️⃣ Delete user
                    cursor.execute(
                        "DELETE FROM users WHERE id = %s",
                        [user_id],
                    )

                    if cursor.rowcount == 0:
                        return Response(
                            {"error": "User not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )

            return Response(
                {"message": "User, all tasks and OTPs deleted"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": "Failed to delete user",
                 "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )