from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Militar, ProfissionalSaude


SYSTEM_USER_PROFILE_OPTIONS = [
    "Administrador",
    "Consultor",
    "Educador Físico",
    "Enfermeiro",
    "Fisioterapeuta",
    "Médico",
    "Nutricionista",
    "Psicopedagogo",
]


class MilitarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Militar
        fields = [
            "id",
            "nr_militar",
            "nome_completo",
            "sexo",
            "turma",
            "posto_graduacao",
            "arma_quadro_servico",
            "curso",
            "companhia",
            "pelotao",
            "is_instrutor",
        ]


class ProfissionalSaudeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfissionalSaude
        fields = [
            "id",
            "militar",
            "especialidade",
            "registro_profissional",
            "ativo",
        ]


class AuthLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)


class AuthUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    is_staff = serializers.BooleanField()


class AuthSessionSerializer(serializers.Serializer):
    is_authenticated = serializers.BooleanField()
    user = AuthUserSerializer(allow_null=True)


class AuthCreateUserSerializer(serializers.Serializer):
    nome_completo = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=254)
    perfil = serializers.ChoiceField(choices=SYSTEM_USER_PROFILE_OPTIONS)
    senha_inicial = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    confirmar_senha_inicial = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    usuario_ativo = serializers.BooleanField(default=True)

    def validate(self, attrs):
        senha_inicial = str(attrs.get("senha_inicial") or "")
        confirmar_senha = str(attrs.get("confirmar_senha_inicial") or "")
        if senha_inicial != confirmar_senha:
            raise serializers.ValidationError({"confirmar_senha_inicial": "As senhas não conferem."})

        email = str(attrs.get("email") or "").strip().lower()
        UserModel = get_user_model()
        if UserModel.objects.filter(username__iexact=email).exists() or UserModel.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "Já existe usuário cadastrado com este e-mail."})

        attrs["email"] = email
        return attrs


class AuthUserDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    perfil = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()

    def get_perfil(self, obj):
        groups = obj.groups.all()
        if groups.exists():
            return str(groups[0].name)
        return "Operador"


class AuthChangePasswordSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    senha_nova = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    confirmar_senha_nova = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs):
        senha_nova = str(attrs.get("senha_nova") or "")
        confirmar_senha = str(attrs.get("confirmar_senha_nova") or "")
        if senha_nova != confirmar_senha:
            raise serializers.ValidationError({"confirmar_senha_nova": "As senhas não conferem."})
        return attrs


class AuthPasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class AuthUpdateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=False)
    usuario_ativo = serializers.BooleanField(required=False)
