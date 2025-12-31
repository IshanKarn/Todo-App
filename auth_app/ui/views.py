import requests
from django.shortcuts import render, redirect

API_BASE = "http://localhost:8000/api"


def register_view(request):
    if request.method == "POST":
        payload = {
            "username": request.POST["username"],
            "email": request.POST["email"],
            "password": request.POST["password"],
        }

        res = requests.post(
            "http://localhost:8000/api/auth/register/",
            json=payload,
        )

        # Safe JSON handling
        try:
            data = res.json()
        except ValueError:
            return render(
                request,
                "auth/register.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        action = data.get("action")

        # Case C & D → Verify email
        if action == "verify_email":
            request.session["pending_email"] = payload["email"]
            return redirect("/auth/verify-email/")

        # Case A & B → Login
        if action == "login":
            return redirect("/auth/login/")

        # Validation / other errors
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

        res = requests.post(f"{API_BASE}/auth/login/", json=payload)
        try:
            data = res.json()
        except ValueError:
            return render(
                request,
                "auth/loggin.html",
                {"error": "Unexpected response from server. Please try again."},
            )
        if res.status_code == 200:
            response = redirect("/tasks")
            response.set_cookie(
                "access_token",
                data["access"],
                httponly=True,
            )
            return response

        return render(
            request,
            "auth/login.html",
            {"error": data.get("error")},
        )

    return render(request, "auth/login.html")

def verify_email_view(request):
    email = request.session.get("pending_email")
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
            return render(
                request,
                "auth/verify_email.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        if res.status_code == 200:
            request.session.pop("pending_email")
            return redirect("/auth/login")

        return render(request, "auth/verify_email.html", {"error": data.get("error")})

    return render(request, "auth/verify_email.html")

def logout_view(request):
    response = redirect("/auth/login")
    response.delete_cookie("access_token")
    return response

def forgot_password_view(request):
    if request.method == "POST":
        res = requests.post(
            "http://localhost:8000/api/auth/forgot-password/",
            json={"email": request.POST["email"]},
        )
        try:
            data = res.json()
        except ValueError:
            return render(
                request,
                "auth/forgot_password.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        if res.status_code == 200:
            request.session["reset_email"] = request.POST["email"]
            return redirect("/auth/reset-password")

        return render(
            request,
            "auth/forgot_password.html",
            {"error": data.get("error")},
        )

    return render(request, "auth/forgot_password.html")

def reset_password_view(request):
    email = request.session.get("reset_email")
    if not email:
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
        except ValueError:
            return render(
                request,
                "auth/reset_password.html",
                {"error": "Unexpected response from server. Please try again."},
            )

        if res.status_code == 200:
            request.session.pop("reset_email")
            return redirect("/auth/login")

        return render(
            request,
            "auth/reset_password.html",
            {"error": data.get("error")},
        )

    return render(request, "auth/reset_password.html")
