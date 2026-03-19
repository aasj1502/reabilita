from rest_framework import serializers

from .models import Militar, ProfissionalSaude


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
