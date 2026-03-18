from datetime import datetime, time
from math import ceil

from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Atendimento, CargaReferenciaHistorico, CargaStatus, EvolucaoMultidisciplinar
from .permissions import IsProfissionalSaude, IsStaffUser
from .serializers import AtendimentoSerializer, CargaReferenciasSerializer, EvolucaoMultidisciplinarSerializer
from .services import load_referencias_saude


class AtendimentoViewSet(ModelViewSet):
    queryset = Atendimento.objects.select_related("cadete", "medico").all()
    serializer_class = AtendimentoSerializer
    permission_classes = [IsAuthenticated, IsProfissionalSaude]


class EvolucaoMultidisciplinarViewSet(ModelViewSet):
    queryset = EvolucaoMultidisciplinar.objects.select_related("atendimento", "profissional").all()
    serializer_class = EvolucaoMultidisciplinarSerializer
    permission_classes = [IsAuthenticated, IsProfissionalSaude]


class CargaReferenciasSaudeView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def post(self, request):
        serializer = CargaReferenciasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resultado = load_referencias_saude(
            reset=serializer.validated_data.get("reset", False),
            force=serializer.validated_data.get("force", False),
        )
        return Response(resultado, status=status.HTTP_200_OK)


class HistoricoCargaReferenciasView(APIView):
    permission_classes = [IsAuthenticated, IsStaffUser]

    def get(self, request):
        page_param = request.query_params.get("page", "1")
        page_size_param = request.query_params.get("page_size") or request.query_params.get("limit", "20")
        order_by_param = (request.query_params.get("order_by") or "criado_em").strip()
        order_dir_param = (request.query_params.get("order_dir") or "desc").strip().lower()

        try:
            page = max(1, int(page_param))
        except ValueError:
            page = 1

        try:
            page_size = max(1, min(int(page_size_param), 100))
        except ValueError:
            page_size = 20

        order_by_allowed = {"id", "status", "criado_em"}
        order_by = order_by_param if order_by_param in order_by_allowed else "criado_em"
        order_dir = "asc" if order_dir_param == "asc" else "desc"
        ordering = order_by if order_dir == "asc" else f"-{order_by}"

        status_param = (request.query_params.get("status") or "").strip().upper()
        data_inicio_param = (request.query_params.get("data_inicio") or "").strip()
        data_fim_param = (request.query_params.get("data_fim") or "").strip()

        historicos = CargaReferenciaHistorico.objects.all()

        status_validos = {escolha for escolha, _label in CargaStatus.choices}
        if status_param and status_param in status_validos:
            historicos = historicos.filter(status=status_param)

        data_inicio = parse_date(data_inicio_param) if data_inicio_param else None
        if data_inicio:
            inicio = timezone.make_aware(datetime.combine(data_inicio, time.min))
            historicos = historicos.filter(criado_em__gte=inicio)

        data_fim = parse_date(data_fim_param) if data_fim_param else None
        if data_fim:
            fim = timezone.make_aware(datetime.combine(data_fim, time.max))
            historicos = historicos.filter(criado_em__lte=fim)

        total = historicos.count()
        total_pages = ceil(total / page_size) if total > 0 else 0
        offset = (page - 1) * page_size

        historicos = historicos.order_by(ordering)[offset : offset + page_size]
        items = [
            {
                "id": item.id,
                "status": item.status,
                "reset": item.reset,
                "force": item.force,
                "arquivos_alterados": item.arquivos_alterados,
                "resumo": item.resumo,
                "mensagem": item.mensagem,
                "criado_em": item.criado_em,
            }
            for item in historicos
        ]

        return Response(
            {
                "items": items,
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_previous": page > 1,
                    "has_next": page < total_pages,
                },
                "ordering": {
                    "order_by": order_by,
                    "order_dir": order_dir,
                },
            },
            status=status.HTTP_200_OK,
        )
