from rest_framework import serializers


class SredAnualItemSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    total_diagnosticos = serializers.IntegerField()


class EficaciaReabilitacaoSerializer(serializers.Serializer):
    percentual_lesoes_sem_retorno_preveniveis = serializers.FloatField()


class PainelClinicoMetricasSerializer(serializers.Serializer):
    cadetes = serializers.IntegerField()
    atendimentos = serializers.IntegerField()
    por_data = serializers.IntegerField()
    retornos = serializers.IntegerField()


class PainelClinicoAtendimentoMesSerializer(serializers.Serializer):
    mes = serializers.CharField()
    total = serializers.IntegerField()


class PainelClinicoEncaminhamentoSerializer(serializers.Serializer):
    perfil = serializers.CharField()
    percentual = serializers.FloatField()
    total = serializers.IntegerField()


class PainelClinicoUltimoAtendimentoSerializer(serializers.Serializer):
    cadete = serializers.CharField()
    data = serializers.DateTimeField()
    tipo = serializers.CharField()
    lesao = serializers.CharField()
    conduta = serializers.CharField()


class PainelClinicoSerializer(serializers.Serializer):
    metricas = PainelClinicoMetricasSerializer()
    atendimentos_ultimos_6_meses = PainelClinicoAtendimentoMesSerializer(many=True)
    encaminhamentos_por_perfil = PainelClinicoEncaminhamentoSerializer(many=True)
    ultimos_atendimentos = PainelClinicoUltimoAtendimentoSerializer(many=True)
