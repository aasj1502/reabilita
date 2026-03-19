from typing import Any, cast

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AuthChangePasswordSerializer,
    AuthCreateUserSerializer,
    AuthLoginSerializer,
    AuthPasswordResetRequestSerializer,
    AuthSessionSerializer,
    AuthUpdateUserSerializer,
    AuthUserDetailSerializer,
)


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


class UserManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not bool(getattr(request.user, "is_staff", False)):
            return Response(
                {"detail": "Apenas administradores podem criar usuários."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AuthCreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        nome_completo = str(validated_data["nome_completo"]).strip()
        email = str(validated_data["email"]).strip().lower()
        perfil = str(validated_data["perfil"]).strip()
        senha_inicial = str(validated_data["senha_inicial"])
        usuario_ativo = bool(validated_data.get("usuario_ativo", True))

        nome_partes = nome_completo.split(maxsplit=1)
        first_name = nome_partes[0] if nome_partes else ""
        last_name = nome_partes[1] if len(nome_partes) > 1 else ""

        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            username=email,
            email=email,
            password=senha_inicial,
            first_name=first_name,
            last_name=last_name,
            is_active=usuario_ativo,
            is_staff=perfil == "Administrador",
        )

        group, _created = Group.objects.get_or_create(name=perfil)
        user.groups.add(group)

        payload = {
            "id": int(getattr(user, "pk", 0) or 0),
            "username": str(getattr(user, "username", "")),
            "email": str(getattr(user, "email", "")),
            "nome_completo": f"{str(getattr(user, 'first_name', '')).strip()} {str(getattr(user, 'last_name', '')).strip()}".strip(),
            "perfil": perfil,
            "is_active": bool(getattr(user, "is_active", False)),
            "is_staff": bool(getattr(user, "is_staff", False)),
        }
        return Response(payload, status=status.HTTP_201_CREATED)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not bool(getattr(request.user, "is_staff", False)):
            return Response(
                {"detail": "Apenas administradores podem listar usuários."},
                status=status.HTTP_403_FORBIDDEN,
            )

        UserModel = get_user_model()
        users = UserModel.objects.all().order_by("username")
        serializer = AuthUserDetailSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id: int):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return Response(
                {"detail": "Usuário não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.pk != request.user.pk and not bool(getattr(request.user, "is_staff", False)):
            return Response(
                {"detail": "Você não tem permissão para visualizar este usuário."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AuthUserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id: int):
        if not bool(getattr(request.user, "is_staff", False)):
            return Response(
                {"detail": "Apenas administradores podem editar usuários."},
                status=status.HTTP_403_FORBIDDEN,
            )

        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return Response(
                {"detail": "Usuário não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AuthUpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        if "email" in validated_data:
            email = str(validated_data["email"]).strip().lower()
            if UserModel.objects.filter(username__iexact=email).exclude(pk=user_id).exists():
                return Response(
                    {"email": "Este e-mail já está em uso."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.email = email
            user.username = email

        if "usuario_ativo" in validated_data:
            user.is_active = bool(validated_data["usuario_ativo"])

        user.save()
        serializer = AuthUserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AuthChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        user = request.user
        senha_atual = str(validated_data["senha_atual"])
        senha_nova = str(validated_data["senha_nova"])

        if not user.check_password(senha_atual):
            return Response(
                {"detail": "Senha atual inválida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(senha_nova)
        user.save()

        return Response(
            {"detail": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = AuthPasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        email = str(validated_data["email"]).strip().lower()
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            return Response(
                {"detail": "Se um usuário com este e-mail existir, um link de recuperação será enviado."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Link de recuperação enviado para o e-mail registrado. Por favor, verifique sua caixa de entrada."},
            status=status.HTTP_200_OK,
        )
