from typing import Any, cast

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AuthLoginSerializer, AuthSessionSerializer


class CsrfTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return Response({"detail": "CSRF cookie definido."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = AuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)
        username = str(validated_data["username"])
        password = str(validated_data["password"])

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {"detail": "Usuário ou senha inválidos."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)

        payload = {
            "is_authenticated": True,
            "user": {
                "id": int(getattr(user, "pk", 0) or 0),
                "username": str(getattr(user, "username", "")),
                "first_name": str(getattr(user, "first_name", "")),
                "last_name": str(getattr(user, "last_name", "")),
                "is_staff": bool(getattr(user, "is_staff", False)),
            },
        }
        return Response(AuthSessionSerializer(payload).data, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        payload = {
            "is_authenticated": True,
            "user": {
                "id": int(getattr(user, "pk", 0) or 0),
                "username": str(getattr(user, "username", "")),
                "first_name": str(getattr(user, "first_name", "")),
                "last_name": str(getattr(user, "last_name", "")),
                "is_staff": bool(getattr(user, "is_staff", False)),
            },
        }
        return Response(AuthSessionSerializer(payload).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Sessão encerrada com sucesso."}, status=status.HTTP_200_OK)
