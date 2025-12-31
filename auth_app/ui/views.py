import requests
from django.shortcuts import render, redirect

from auth_app.logger import auth_ui_logger

API_BASE = "http://localhost:8000/api"


def register_view(request):
    if request.method == "POST":
        payload = {
            "username": request.POST["username"],
            "email": request.POST["email"],
            "password": request.POST["password"],
        }

        auth_ui_logger.info(
            f"UI_REGISTER_SUBMIT | email={payload['email']}"
        )

        res = requests.post(
            "http://localhost:8000/api/auth/register/",
            json=payload,
        )

        # Safe JSON handling
        try:
            data = res.json()
        except ValueError:
            auth_ui_logger.warning(
                f"UI_REGISTER_ERROR | email={payload['email']}"
            )

            return render(
                request,
                "auth/register.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        action = data.get("action")

        # Case C & D → Verify email
        if action == "verify_email":
            auth_ui_logger.info(
                "UI_REGISTER_REDIRECT | to=verify_email"
            )
            request.session["pending_email"] = payload["email"]
            return redirect("/auth/verify-email/")

        # Case A & B → Login
        if action == "login":
            auth_ui_logger.info(
                "UI_REGISTER_REDIRECT | to=login"
            )
            return redirect("/auth/login/")

        # Validation / other errors
        auth_ui_logger.info(
            "UI_REGISTER_ERROR | error=validation"
        )
        return render(
            request,
            "auth/register.html",
            {"error": data.get("error", "Registration failed")},
        )

    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        payload = {
            "username_or_email": request.POST["username_or_email"],
            "password": request.POST["password"],
        }
        auth_ui_logger.info(
            f"UI_LOGIN_SUBMIT | identifier={payload['username_or_email']}"
        )

        res = requests.post(f"{API_BASE}/auth/login/", json=payload)
        try:
            data = res.json()
        except ValueError:
            auth_ui_logger.warning(
                f"UI_LOGIN_RESPONSE_ERROR | identifier={payload['username_or_email']}"
            )
            return render(
                request,
                "auth/loggin.html",
                {"error": "Unexpected response from server. Please try again."},
            )
        if res.status_code == 200:
            auth_ui_logger.info(
                f"UI_LOGIN_SUCCESS | identifier={payload['username_or_email']}"
            )
            response = redirect("/tasks")
            response.set_cookie(
                "access_token",
                data["access"],
                httponly=True,
            )
            return response

        auth_ui_logger.warning(
            f"UI_LOGIN_ERROR | identifier={payload['username_or_email']}"
        )
        return render(
            request,
            "auth/login.html",
            {"error": data.get("error")},
        )
    auth_ui_logger.info(
        f"UI_LOGIN | Form Retrieved"
    )
    return render(request, "auth/login.html")

def verify_email_view(request):
    email = request.session.get("pending_email")
    auth_ui_logger.info(
        f"UI_VERIFY_EMAIL_SUBMIT | identifier={payload['email']}"
    )
    if not email:
        return redirect("/auth/register")

    if request.method == "POST":
        payload = {
            "email": email,
            "otp": request.POST["otp"],
        }

        res = requests.post(
            "http://localhost:8000/api/auth/verify-email/",
            json=payload,
        )
        try:
            data = res.json()
        except ValueError:
            auth_ui_logger.warning(
                f"UI_VERIFY_EMAIL_RESPONSE_ERROR | identifier={payload['email']}"
            )
            return render(
                request,
                "auth/verify_email.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        if res.status_code == 200:
            auth_ui_logger.info(
                f"UI_VERIFY_EMAIL_SUCCESS | identifier={payload['email']}"
            )
            request.session.pop("pending_email")
            return redirect("/auth/login")

        auth_ui_logger.warning(
            f"UI_VERIFY_EMAIL_ERROR | identifier={payload['email']}"
        )
        return render(request, "auth/verify_email.html", {"error": data.get("error")})

    auth_ui_logger.info(
        f"UI_VERIFY_EMAIL | Form Retrieved"
    )
    return render(request, "auth/verify_email.html")

def logout_view(request):
    auth_ui_logger.info(
        "UI_LOGOUT | redirect=login"
    )

    response = redirect("/auth/login")
    response.delete_cookie("access_token")
    return response

def forgot_password_view(request):
    if request.method == "POST":
        res = requests.post(
            "http://localhost:8000/api/auth/forgot-password/",
            json={"email": request.POST["email"]},
        )
        auth_ui_logger.info(
            f"UI_FORGOT_PASSWORD_SUBMIT | email={request.POST["email"]}"
        )
        try:
            data = res.json()
        except ValueError as e:
            auth_ui_logger.warning(
                f"UI_FORGOT_PASSWORD_RESPONSE_ERROR | email={request.POST["email"]} error={str(e)}"
            )
            return render(
                request,
                "auth/forgot_password.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        if res.status_code == 200:
            auth_ui_logger.info(
                f"UI_FORGOT_PASSWORD_SUCCESS | email={request.POST["email"]} redirect=reset-password"
            )
            request.session["reset_email"] = request.POST["email"]
            return redirect("/auth/reset-password")

        auth_ui_logger.warning(
            f"UI_FORGOT_PASSWORD_ERROR | error={data.get("error")}"
        )
        return render(
            request,
            "auth/forgot_password.html",
            {"error": data.get("error")},
        )

    auth_ui_logger.info(
        f"UI_FORGOT_PASSWORD | Form Retrieved"
    )
    return render(request, "auth/forgot_password.html")

def reset_password_view(request):
    email = request.session.get("reset_email")
    auth_ui_logger.info(
        f"UI_RESET_PASSWORD_ATTEMPT | email={email}"
    )
    if not email:
        auth_ui_logger.info(
            f"UI_RESET_PASSWORD_ATTEMPT | error=missing_email redirect=forgot-password"
        )
        return redirect("/auth/forgot-password")

    if request.method == "POST":
        payload = {
            "email": email,
            "otp": request.POST["otp"],
            "new_password": request.POST["new_password"],
        }

        res = requests.post(
            "http://localhost:8000/api/auth/reset-password/",
            json=payload,
        )

        try:
            data = res.json()
        except ValueError as e:
            auth_ui_logger.info(
                f"UI_RESET_PASSWORD_ERROR | email={email} error={str(e)}"
            )
            return render(
                request,
                "auth/reset_password.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        if res.status_code == 200:
            auth_ui_logger.info(
                f"UI_RESET_PASSWORD_SUCCESS | email={email}"
            )
            request.session.pop("reset_email")
            return redirect("/auth/login")

        auth_ui_logger.warning(
            f"UI_RESET_PASSWORD_ERROR | email={email} error={data.get("error")}"
        )
        return render(
            request,
            "auth/reset_password.html",
            {"error": data.get("error")},
        )

    return render(request, "auth/reset_password.html")
