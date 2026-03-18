from rest_framework import serializers

from apps.pessoal.models import Militar, ProfissionalSaude
from .models import Atendimento, EvolucaoMultidisciplinar


class CargaReferenciasSerializer(serializers.Serializer):
    reset = serializers.BooleanField(default=False)
    force = serializers.BooleanField(default=False)


class AtendimentoSerializer(serializers.ModelSerializer):
    cadete_id = serializers.PrimaryKeyRelatedField(source="cadete", queryset=Militar.objects.all())
    medico_id = serializers.PrimaryKeyRelatedField(source="medico", queryset=ProfissionalSaude.objects.all())

    class Meta:
        model = Atendimento
        fields = [
            "id",
            "data_registro",
            "cadete_id",
            "medico_id",
            "tipo_lesao",
            "origem_lesao",
            "estrutura_anatomica",
            "lateralidade",
            "codigo_cid10",
            "codigo_cido",
            "flag_sred",
        ]
        read_only_fields = ["id", "data_registro", "flag_sred"]


class EvolucaoMultidisciplinarSerializer(serializers.ModelSerializer):
    atendimento_id = serializers.PrimaryKeyRelatedField(source="atendimento", queryset=Atendimento.objects.all())
    profissional_id = serializers.PrimaryKeyRelatedField(source="profissional", queryset=ProfissionalSaude.objects.all())

    class Meta:
        model = EvolucaoMultidisciplinar
        fields = [
            "id",
            "atendimento_id",
            "profissional_id",
            "parecer_tecnico",
            "data_evolucao",
        ]
        read_only_fields = ["id", "data_evolucao"]
