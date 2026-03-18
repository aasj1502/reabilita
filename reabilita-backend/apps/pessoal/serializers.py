from rest_framework import serializers

from .models import Militar, ProfissionalSaude


class MilitarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Militar
        fields = [
            "id",
            "nr_militar",
            "nome_completo",
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
