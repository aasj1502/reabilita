from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import EspecialidadeMedica, FuncaoInstrutor, Militar, ProfissionalSaude, UserProfile


ESPECIALIDADE_MEDICA_OPTIONS = [c[0] for c in EspecialidadeMedica.choices]
FUNCAO_INSTRUTOR_OPTIONS = [c[0] for c in FuncaoInstrutor.choices]

SYSTEM_USER_PROFILE_OPTIONS = [
    "Administrador",
    "Consultor",
    "Educador Físico",
    "Enfermeiro",
    "Fisioterapeuta",
    "Instrutor",
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
            "nome_guerra",
            "sexo",
            "turma",
            "ano",
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
    especialidade_medica = serializers.ChoiceField(
        choices=ESPECIALIDADE_MEDICA_OPTIONS, required=False, allow_blank=True, default="",
    )
    funcao_instrutor = serializers.ChoiceField(
        choices=FUNCAO_INSTRUTOR_OPTIONS, required=False, allow_blank=True, default="",
    )
    posto_graduacao = serializers.CharField(max_length=80, required=False, allow_blank=True, default="")
    nome_guerra = serializers.CharField(max_length=80, required=False, allow_blank=True, default="")
    setor = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    fracao = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    senha_inicial = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    confirmar_senha_inicial = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)
    usuario_ativo = serializers.BooleanField(default=True)

    def validate(self, attrs):
        senha_inicial = str(attrs.get("senha_inicial") or "")
        confirmar_senha = str(attrs.get("confirmar_senha_inicial") or "")
        if senha_inicial != confirmar_senha:
            raise serializers.ValidationError({"confirmar_senha_inicial": "As senhas não conferem."})

        perfil = str(attrs.get("perfil") or "")
        especialidade = str(attrs.get("especialidade_medica") or "").strip()
        if perfil == "Médico" and not especialidade:
            raise serializers.ValidationError({"especialidade_medica": "Selecione a especialidade médica."})
        if perfil != "Médico" and especialidade:
            attrs["especialidade_medica"] = ""

        funcao = str(attrs.get("funcao_instrutor") or "").strip()
        if perfil == "Instrutor" and not funcao:
            raise serializers.ValidationError({"funcao_instrutor": "Selecione a função do instrutor."})
        if perfil != "Instrutor" and funcao:
            attrs["funcao_instrutor"] = ""

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
    especialidade_medica = serializers.SerializerMethodField()
    funcao_instrutor = serializers.SerializerMethodField()
    posto_graduacao = serializers.SerializerMethodField()
    nome_guerra = serializers.SerializerMethodField()
    setor = serializers.SerializerMethodField()
    fracao = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()

    def _get_profile(self, obj):
        profile = getattr(obj, "_cached_profile", None)
        if profile is not None:
            return profile
        profile = getattr(obj, "profile", None)
        if profile is None:
            try:
                profile = UserProfile.objects.get(user=obj)
            except UserProfile.DoesNotExist:
                profile = None
        obj._cached_profile = profile
        return profile

    def get_perfil(self, obj):
        groups = obj.groups.all()
        if groups.exists():
            return str(groups[0].name)
        return "Operador"

    def get_especialidade_medica(self, obj):
        profile = self._get_profile(obj)
        return (profile.especialidade_medica or "") if profile else ""

    def get_funcao_instrutor(self, obj):
        profile = self._get_profile(obj)
        return (profile.funcao_instrutor or "") if profile else ""

    def get_posto_graduacao(self, obj):
        profile = self._get_profile(obj)
        return (profile.posto_graduacao or "") if profile else ""

    def get_nome_guerra(self, obj):
        profile = self._get_profile(obj)
        return (profile.nome_guerra or "") if profile else ""

    def get_setor(self, obj):
        profile = self._get_profile(obj)
        return (profile.setor or "") if profile else ""

    def get_fracao(self, obj):
        profile = self._get_profile(obj)
        return (profile.fracao or "") if profile else ""


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
