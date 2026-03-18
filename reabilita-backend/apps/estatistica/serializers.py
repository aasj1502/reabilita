from rest_framework import serializers


class SredAnualItemSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    total_diagnosticos = serializers.IntegerField()


class EficaciaReabilitacaoSerializer(serializers.Serializer):
    percentual_lesoes_sem_retorno_preveniveis = serializers.FloatField()
