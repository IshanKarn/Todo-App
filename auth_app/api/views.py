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

from auth_app.logger import auth_api_logger

class RegisterAPI(APIView):

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        auth_api_logger.info(
            f"REGISTER_ATTEMPT | username={username} email={email}"
        )

        if not username or not email or not password:
            return Response(
                {"error": "All fields required"},
                status=400,
            )

        if not is_valid_email(email):
            auth_api_logger.warning(
                f"REGISTER_BLOCKED | invalid_email={email}"
            )
            return Response(
                {"error": "Invalid email format"},
                status=400,
            )

        with connection.cursor() as cursor:
            # Check email status
            cursor.execute(
                """
                SELECT id, is_email_verified
                FROM users
                WHERE email = %s
                """,
                [email],
            )
            email_row = cursor.fetchone()

            # CASE — Email exists
            if email_row:
                user_id, is_email_verified = email_row

                # CASE — Email verified - Login
                if is_email_verified:
                    auth_api_logger.warning(
                        f"REGISTER_BLOCKED | verified_email_exists={email}"
                    )
                    return Response(
                        {
                            "error": "Email already registered",
                            "email_verified": True,
                            "action": "login",
                        },
                        status=409,
                    )

                # CASE — Email exists but NOT verified → resend OTP
                otp = str(random.randint(100000, 999999))
                expiry = datetime.utcnow() + timedelta(minutes=5)

                cursor.execute(
                    """
                    INSERT INTO password_otps (user_id, otp, expires_at)
                    VALUES (%s, %s, %s)
                    """,
                    [user_id, otp, expiry],
                )

                auth_api_logger.warning(
                    f"REGISTER_BLOCKED | email_exists={email}"
                )

                send_mail(
                    "Verify your email",
                    f"Your verification OTP is {otp}. Valid for 5 minutes.",
                    None,
                    [email],
                )

                return Response(
                    {
                        "message": "Email already registered but not verified",
                        "email_verified": False,
                        "action": "verify_email",
                    },
                    status=200,
                )

            # Case - Username exists
            cursor.execute(
                "SELECT 1 FROM users WHERE username = %s",
                [username],
            )
            username_row = cursor.fetchone()
            if username_row:
                auth_api_logger.warning(
                    f"REGISTER_BLOCKED | username_exists={username}"
                )
                return Response(
                    {
                        "error": "Username already exists"
                    },
                    status=409,
                )
            
            # CASE — New user registration
            
            otp = str(random.randint(100000, 999999))
            expiry = datetime.utcnow() + timedelta(minutes=5)

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

        auth_api_logger.info(
            f"REGISTER_OTP_SENT | email={email}"
        )

        return Response(
            {
                "message": "OTP sent to email",
                "action": "verify_email",
            },
            status=200,
        )


class VerifyEmailOTP(APIView):

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        auth_api_logger.info(
            f"VERIFY_EMAIL_ATTEMPT | identifier={email}"
        )

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
                auth_api_logger.info(
                    f"VERIFY_EMAIL_INVALID_OTP | identifier={email}"
                )
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
        
        auth_api_logger.info(
            f"VERIFY_EMAIL_SUCCESS | identifier={email}"
        )

        return Response({"message": "Email verified"})


class LoginAPI(APIView):

    def post(self, request):
        username_or_email = request.data.get("username_or_email")
        password = request.data.get("password")

        auth_api_logger.info(
            f"LOGIN_ATTEMPT | username_or_email={username_or_email}"
        )

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
            auth_api_logger.warning(
                f"LOGIN_FAILED | username_or_email={username_or_email}"
            )
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id, hashed_password, email, is_email_verified = user

        # Password incorrect
        if not verify_password(password, hashed_password):
            auth_api_logger.warning(
                f"LOGIN_FAILED | user_id={user_id} reason=wrong_password"
            )
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

            auth_api_logger.info(
                f"LOGIN_BLOCKED_EMAIL_NOT_VERIFIED | user_id={user_id}"
            )

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

        auth_api_logger.info(
            f"LOGIN_SUCCESS | user_id={user_id}"
        )

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
        auth_api_logger.info(
            f"LOGOUT_SUCCESS | logout successful"
        )
        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )


    
class ForgotPasswordAPI(APIView):

    def post(self, request):
        email = request.data.get("email")

        auth_api_logger.info(
            f"FORGOT_PASSWORD_ATTEMPT | email={email}"
        )

        otp = str(random.randint(100000, 999999))
        expiry = datetime.utcnow() + timedelta(minutes=5)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE email=%s AND is_email_verified=1",
                [email],
            )
            user = cursor.fetchone()

            if not user:
                auth_api_logger.info(
                    f"FORGOT_PASSWORD_INVALID_EMAIL | email={email}"
                )
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

        auth_api_logger.info(
            f"FORGOT_PASSWORD_OTP_SENT | email={email}"
        )

        return Response({"message": "OTP sent"})

class ResetPasswordOTP(APIView):

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        auth_api_logger.info(
            f"RESET_PASSWORD_ATTEMPT | email={email}"
        )

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
                auth_api_logger.warning(
                    f"RESET_PASSWORD_INVALID_OTP | email={email}"
                )
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
            auth_api_logger.warning(
                f"RESET_PASSWORD_SUCCESS | email={email}"
            )
        return Response({"message": "Password reset successful"})


class DeleteUserCascadeAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsJWTAuthenticated]

    def delete(self, request):
        user_id = request.user["user_id"]
        auth_api_logger.info(
            f"USER_DELETE_ATTEMPT | user_id={user_id} cascade=true"
        )
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # 1️⃣ Delete tasks first
                    cursor.execute(
                        "DELETE FROM tasks WHERE user_id = %s",
                        [user_id],
                    )
                    auth_api_logger.info(
                        f"USER_TASKS_DELETED | user_id={user_id}"
                    )

                    # 2️⃣ Delete password otps
                    cursor.execute(
                        "DELETE FROM password_otps  WHERE user_id = %s",
                        [user_id],
                    )
                    auth_api_logger.info(
                        f"USER_OTPS_DELETED | user_id={user_id}"
                    )

                    # 2️⃣ Delete user
                    cursor.execute(
                        "DELETE FROM users WHERE id = %s",
                        [user_id],
                    )
                    auth_api_logger.warning(
                        f"USER_DELETED | user_id={user_id}"
                    )

                    if cursor.rowcount == 0:
                        return Response(
                            {"error": "User not found"},
                            status=status.HTTP_404_NOT_FOUND,
                        )
            auth_api_logger.warning(
                f"USER_DELETED | user_id={user_id} cascade=true"
            )
            return Response(
                {"message": "User, all tasks and OTPs deleted"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            auth_api_logger.warning(
                f"USER_DELETE_ERROR | user_id={user_id} error={e}"
            )
            return Response(
                {"error": "Failed to delete user",
                 "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )