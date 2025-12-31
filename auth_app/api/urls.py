from django.urls import path

from .views import (
    RegisterAPI,
    VerifyEmailOTP,
    LoginAPI,
    ForgotPasswordAPI,
    ResetPasswordOTP,
    DeleteUserCascadeAPI,
    LogoutAPI,
)


urlpatterns = [
    path("register/", RegisterAPI.as_view()),
    path("verify-email/", VerifyEmailOTP.as_view()),
    path("login/", LoginAPI.as_view()),
    path("forgot-password/", ForgotPasswordAPI.as_view()),
    path("reset-password/", ResetPasswordOTP.as_view()),
    path("delete-user/", DeleteUserCascadeAPI.as_view()),
    path("logout/", LogoutAPI.as_view()),
]