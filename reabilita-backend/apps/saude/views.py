from datetime import datetime, time
from math import ceil

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import (
    Atendimento,
    CargaReferenciaHistorico,
    CargaStatus,
    Cid10Categoria,
    CidOMorfologia,
    EvolucaoMultidisciplinar,
    OrigemLesao,
    SaudeReferenciaLesao,
    TipoLesao,
)
from .permissions import IsProfissionalSaude, IsStaffUser
from .references import (
    DECISAO_SRED_OPTIONS,
    DISPOSICAO_OPTIONS,
    ENCAMINHAMENTOS_OPTIONS,
    EXAMES_COMPLEMENTARES_OPTIONS,
    TIPO_ATENDIMENTO_OPTIONS,
    build_atividade_contexto_options,
    build_sac_reference_maps,
)
from .serializers import (
    AtendimentoSerializer,
    CargaReferenciasSerializer,
    EvolucaoMultidisciplinarSerializer,
    SaudeReferenciaLesaoSerializer,
)
from .services import load_referencias_saude


class AtendimentoViewSet(ModelViewSet):
    queryset = Atendimento.objects.select_related("cadete", "medico").all()
    serializer_class = AtendimentoSerializer
    permission_classes = [IsAuthenticated, IsProfissionalSaude]


class EvolucaoMultidisciplinarViewSet(ModelViewSet):
    queryset = EvolucaoMultidisciplinar.objects.select_related("atendimento", "profissional").all()
    serializer_class = EvolucaoMultidisciplinarSerializer
    permission_classes = [IsAuthenticated, IsProfissionalSaude]


class AtendimentoReferenciasView(APIView):
    permission_classes = [IsAuthenticated, IsProfissionalSaude]

    def get(self, request):
        sac_maps = build_sac_reference_maps()
        atividade_contexto = build_atividade_contexto_options()

        return Response(
            {
                "tipo_atendimento_options": TIPO_ATENDIMENTO_OPTIONS,
                "tipo_lesao_options": [escolha for escolha, _label in TipoLesao.choices],
                "origem_lesao_options": [escolha for escolha, _label in OrigemLesao.choices],
                "decisao_sred_options": DECISAO_SRED_OPTIONS,
                "exames_complementares_options": EXAMES_COMPLEMENTARES_OPTIONS,
                "encaminhamentos_options": ENCAMINHAMENTOS_OPTIONS,
                "disposicao_options": DISPOSICAO_OPTIONS,
                **atividade_contexto,
                **sac_maps,
            },
            status=status.HTTP_200_OK,
        )


class Cid10AutocompleteView(APIView):
    permission_classes = [IsAuthenticated, IsProfissionalSaude]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        limit_param = request.query_params.get("limit", "15")

        try:
            limit = max(1, min(int(limit_param), 50))
        except ValueError:
            limit = 15

        queryset = Cid10Categoria.objects.all()
        if query:
            queryset = queryset.filter(Q(codigo__icontains=query) | Q(descricao__icontains=query))

        items = [
            {
                "codigo": item.codigo,
                "descricao": item.descricao,
            }
            for item in queryset.order_by("codigo")[:limit]
        ]

        return Response({"items": items}, status=status.HTTP_200_OK)


class CidOAutocompleteView(APIView):
    permission_classes = [IsAuthenticated, IsProfissionalSaude]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        limit_param = request.query_params.get("limit", "15")

        try:
            limit = max(1, min(int(limit_param), 50))
        except ValueError:
            limit = 15

        queryset = CidOMorfologia.objects.all()
        if query:
            queryset = queryset.filter(Q(codigo__icontains=query) | Q(descricao__icontains=query))

        items = [
            {
                "codigo": item.codigo,
                "descricao": item.descricao,
                "referencia": item.referencia,
            }
            for item in queryset.order_by("codigo")[:limit]
        ]

        return Response({"items": items}, status=status.HTTP_200_OK)


class SaudeReferenciaLesaoListView(APIView):
    """Retorna referências de lesão com filtro hierárquico."""

    permission_classes = [IsAuthenticated, IsProfissionalSaude]

    def get(self, request):
        qs = SaudeReferenciaLesao.objects.all()

        tipo_tecido = (request.query_params.get("tipo_tecido") or "").strip()
        regiao_geral = (request.query_params.get("regiao_geral") or "").strip()
        sub_regiao = (request.query_params.get("sub_regiao") or "").strip()

        if tipo_tecido:
            qs = qs.filter(tipo_tecido=tipo_tecido)
        if regiao_geral:
            qs = qs.filter(regiao_geral=regiao_geral)
        if sub_regiao:
            qs = qs.filter(sub_regiao=sub_regiao)

        serializer = SaudeReferenciaLesaoSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SaudeReferenciaLesaoLookupView(APIView):
    """Busca (ou cria) uma SaudeReferenciaLesao com base nos 4 campos."""

    permission_classes = [IsAuthenticated, IsProfissionalSaude]

    def post(self, request):
        serializer = SaudeReferenciaLesaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, created = SaudeReferenciaLesao.objects.get_or_create(
            tipo_tecido=serializer.validated_data["tipo_tecido"],
            regiao_geral=serializer.validated_data["regiao_geral"],
            sub_regiao=serializer.validated_data["sub_regiao"],
            item_especifico=serializer.validated_data["item_especifico"],
        )
        result = SaudeReferenciaLesaoSerializer(obj)
        return Response(
            {"referencia": result.data, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SaudeReferenciaLesaoHierarquiaView(APIView):
    """Retorna a hierarquia disponível: tipos, regiões, sub-regiões."""

    permission_classes = [IsAuthenticated, IsProfissionalSaude]

    def get(self, request):
        tipo_tecido = (request.query_params.get("tipo_tecido") or "").strip()
        regiao_geral = (request.query_params.get("regiao_geral") or "").strip()
        sub_regiao = (request.query_params.get("sub_regiao") or "").strip()

        qs = SaudeReferenciaLesao.objects.all()

        tipos = sorted(qs.values_list("tipo_tecido", flat=True).distinct())

        regioes = []
        if tipo_tecido:
            regioes = sorted(
                qs.filter(tipo_tecido=tipo_tecido)
                .values_list("regiao_geral", flat=True)
                .distinct()
            )

        sub_regioes = []
        if tipo_tecido and regiao_geral:
            sub_regioes = sorted(
                qs.filter(tipo_tecido=tipo_tecido, regiao_geral=regiao_geral)
                .values_list("sub_regiao", flat=True)
                .distinct()
            )

        itens = []
        if tipo_tecido and regiao_geral and sub_regiao:
            itens = sorted(
                qs.filter(
                    tipo_tecido=tipo_tecido,
                    regiao_geral=regiao_geral,
                    sub_regiao=sub_regiao,
                )
                .values_list("item_especifico", flat=True)
                .distinct()
            )

        return Response(
            {
                "tipos_tecido": tipos,
                "regioes_gerais": regioes,
                "sub_regioes": sub_regioes,
                "itens_especificos": itens,
            },
            status=status.HTTP_200_OK,
        )


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
