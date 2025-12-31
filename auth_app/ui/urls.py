from django.urls import path

from .views import (
    register_view,
    verify_email_view,
    login_view,
    forgot_password_view,
    reset_password_view,
    logout_view,
)


urlpatterns = [
    path("register/", register_view),
    path("verify-email/", verify_email_view),
    path("login/", login_view),
    path("forgot-password/", forgot_password_view),
    path("reset-password/", reset_password_view),
    path("logout/", logout_view),
]