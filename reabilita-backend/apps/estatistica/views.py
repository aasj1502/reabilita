from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsEquipeSaudeOuStaff


class SredAnualView(APIView):
    permission_classes = [IsAuthenticated, IsEquipeSaudeOuStaff]

    def get(self, request):
        return Response({"items": []})


class EficaciaReabilitacaoView(APIView):
    permission_classes = [IsAuthenticated, IsEquipeSaudeOuStaff]

    def get(self, request):
        return Response({"percentual_lesoes_sem_retorno_preveniveis": 0.0})
