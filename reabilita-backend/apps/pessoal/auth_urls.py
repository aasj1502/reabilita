from django.urls import path

from .auth_views import (
    ChangePasswordView,
    CsrfTokenView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetRequestView,
    UserDetailView,
    UserListView,
    UserManagementView,
)

urlpatterns = [
    path("csrf/", CsrfTokenView.as_view(), name="auth-csrf"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("usuarios/", UserListView.as_view(), name="auth-usuarios-list"),
    path("usuarios/novo/", UserManagementView.as_view(), name="auth-usuarios-create"),
    path("usuarios/<int:user_id>/", UserDetailView.as_view(), name="auth-usuarios-detail"),
    path("mudar-senha/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("recuperar-senha/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
]
