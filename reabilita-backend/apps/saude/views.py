from datetime import datetime, time
import csv
import io
from math import ceil

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.parsers import MultiPartParser
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
    DecisaoSred,
    EvolucaoMultidisciplinar,
    Lateralidade,
    OrigemLesao,
    SaudeReferenciaLesao,
    TipoAtendimento,
    TipoLesao,
)
from .permissions import IsProfissionalSaude, IsStaffUser
from .references import (
    DECISAO_SRED_OPTIONS,
    DISPOSICAO_OPTIONS,
    ENCAMINHAMENTOS_OPTIONS,
    EXAMES_COMPLEMENTARES_OPTIONS,
    ORIGEM_LESAO_NORMALIZE,
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


# ────────────────────────── Importação CSV ──────────────────────────────────

_CONDUTA_MAP = {
    "Conservador": "Conservador",
    "PósOperatório": "Pós-operatório",
    "Cirúrgico": "Cirúrgico",
    "Aguardar Exame": "Aguardando Exame",
}

_CAUSA_MAP = {
    "Previnível": "Prevenível",
    "Decorrente da Atividade": "Decorrente da Atividade",
}

_SRED_MAP = {
    "Confirmada": DecisaoSred.POSITIVO,
    "Iniciar investigação": DecisaoSred.POSITIVO,
    "Não investigar": DecisaoSred.NEGATIVO,
}

_EXAMES_COLS = ["RX", "USG", "TC", "RM", "DEXA", "Sangue"]
_ENC_MAP = {
    "Fisioterapia": "Fisioterapia",
    "SEF": "Educador Físico",
    "Nutricionista": "Nutricionista",
    "Psicopedagógica": "Psicopedagogo",
}
_DISP_MAP = {
    "Dispensa": "Dispensado",
    "VCL": "VCL",
    "Alta": "Alta",
    "Risco Cirúrgico": "Risco Cirúrgico",
}


def _parse_csv_date(text: str):
    """Parse DD/MM/YYYY ou MM/DD/YYYY, retorna date ou None."""
    from datetime import date as _date
    text = text.strip()
    if not text:
        return None
    parts = text.split("/")
    if len(parts) != 3:
        return None
    a, b, y = int(parts[0]), int(parts[1]), int(parts[2])
    try:
        return _date(y, b, a)
    except ValueError:
        pass
    try:
        return _date(y, a, b)
    except ValueError:
        return None


def _validate_csv_row(row: dict, line_num: int) -> list[str]:
    """Retorna lista de erros para uma linha do CSV."""
    erros = []
    tipo_lesao = row.get("Lesão", "").strip()
    if tipo_lesao and tipo_lesao not in {c.value for c in TipoLesao}:
        erros.append(f"Linha {line_num}: tipo_lesao inválido '{tipo_lesao}'")

    data_raw = row.get("Data", "").strip()
    if data_raw and _parse_csv_date(data_raw) is None:
        erros.append(f"Linha {line_num}: data inválida '{data_raw}'")

    atendimento_tipo = row.get("Atendimento", "").strip()
    if atendimento_tipo and atendimento_tipo not in {"Inicial", "Retorno"}:
        erros.append(f"Linha {line_num}: tipo atendimento inválido '{atendimento_tipo}'")

    return erros


class ImportarCSVPreviewView(APIView):
    """Faz upload de CSV e retorna preview + erros de validação sem persistir."""
    permission_classes = [IsAuthenticated, IsStaffUser]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivo = request.FILES.get("arquivo")
        if not arquivo:
            return Response(
                {"detail": "Envie um arquivo CSV no campo 'arquivo'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if arquivo.size > 5 * 1024 * 1024:
            return Response(
                {"detail": "Arquivo excede o limite de 5 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            conteudo = arquivo.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                arquivo.seek(0)
                conteudo = arquivo.read().decode("latin-1")
            except Exception:
                return Response(
                    {"detail": "Não foi possível decodificar o arquivo."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        separador = ";" if ";" in conteudo.split("\n")[0] else ","
        reader = csv.DictReader(io.StringIO(conteudo), delimiter=separador)
        rows = list(reader)

        erros: list[str] = []
        preview: list[dict] = []
        for idx, row in enumerate(rows):
            line_num = idx + 2
            row_erros = _validate_csv_row(row, line_num)
            erros.extend(row_erros)
            if idx < 20:
                preview.append({
                    "linha": line_num,
                    "data": row.get("Data", ""),
                    "atendimento": row.get("Atendimento", ""),
                    "lesao": row.get("Lesão", ""),
                    "parte_corpo": row.get("Parte do Corpo", ""),
                    "parte_lesionada": row.get("Parte Lesionada", ""),
                    "origem": row.get("Origem da Lesão", ""),
                    "erros": row_erros,
                })

        return Response({
            "total_linhas": len(rows),
            "total_erros": len(erros),
            "erros": erros[:50],
            "preview": preview,
            "colunas_detectadas": list(reader.fieldnames or []),
        })


class ImportarCSVConfirmarView(APIView):
    """Recebe o CSV e persiste os atendimentos no banco."""
    permission_classes = [IsAuthenticated, IsStaffUser]
    parser_classes = [MultiPartParser]

    def post(self, request):
        from apps.pessoal.models import Militar, ProfissionalSaude

        arquivo = request.FILES.get("arquivo")
        if not arquivo:
            return Response(
                {"detail": "Envie um arquivo CSV no campo 'arquivo'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if arquivo.size > 5 * 1024 * 1024:
            return Response(
                {"detail": "Arquivo excede o limite de 5 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            conteudo = arquivo.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                arquivo.seek(0)
                conteudo = arquivo.read().decode("latin-1")
            except Exception:
                return Response(
                    {"detail": "Não foi possível decodificar o arquivo."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        separador = ";" if ";" in conteudo.split("\n")[0] else ","
        reader = csv.DictReader(io.StringIO(conteudo), delimiter=separador)
        rows = list(reader)

        erros: list[str] = []
        for idx, row in enumerate(rows):
            erros.extend(_validate_csv_row(row, idx + 2))
        if erros:
            return Response(
                {"detail": "CSV contém erros de validação.", "erros": erros[:50]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Médico padrão
        from apps.pessoal.models import Militar as MilitarModel, ProfissionalSaude as ProfModel
        medico_nome = request.data.get("medico_nome", "1 Ten Real")
        medico_mil, _ = MilitarModel.objects.get_or_create(
            nr_militar="MED_001",
            defaults={
                "nome_completo": medico_nome,
                "nome_guerra": medico_nome.split()[-1],
                "sexo": "M",
                "posto_graduacao": "1º Tenente",
            },
        )
        medico, _ = ProfModel.objects.get_or_create(
            militar=medico_mil,
            defaults={"especialidade": "Médico", "ativo": True},
        )

        # Processar linhas
        from datetime import date as _date, time as _time, datetime as _dt, timezone as _tz

        atendimentos: list[Atendimento] = []
        cadete_counter = MilitarModel.objects.filter(nr_militar__startswith="CAD_").count()
        avisos: list[str] = []

        for idx, row in enumerate(rows):
            d = _parse_csv_date(row.get("Data", ""))
            if d is None:
                avisos.append(f"Linha {idx + 2}: data inválida, ignorada")
                continue

            hora_parts = (row.get("Hora", "") or "").strip().split(":")
            h = int(hora_parts[0]) if len(hora_parts) > 0 and hora_parts[0] else 0
            m = int(hora_parts[1]) if len(hora_parts) > 1 else 0
            t = _time(h, m, 0)
            dt = _dt.combine(d, t, tzinfo=_tz.utc)

            tipo_atend = row.get("Atendimento", "").strip()
            if tipo_atend not in {"Inicial", "Retorno"}:
                tipo_atend = "Inicial"

            tipo_lesao = row.get("Lesão", "").strip()
            if tipo_lesao not in {c.value for c in TipoLesao}:
                avisos.append(f"Linha {idx + 2}: tipo_lesao inválido, ignorada")
                continue

            cadete_counter += 1
            nr = f"CAD_{cadete_counter:04d}"
            sexo = row.get("Sexo", "M").strip() or "M"
            cadete, _ = MilitarModel.objects.get_or_create(
                nr_militar=nr,
                defaults={
                    "nome_completo": f"Cadete {cadete_counter:04d}",
                    "nome_guerra": f"Cadete{cadete_counter:04d}",
                    "sexo": sexo,
                },
            )

            origem_raw = row.get("Origem da Lesão", "").strip()
            origem_normalizada = ORIGEM_LESAO_NORMALIZE.get(origem_raw.lower(), "")

            segmento = row.get("Parte do Corpo", "").strip()
            estrutura = row.get("Parte Lesionada", "").strip()
            localizacao = row.get("Local da Lesão", "").strip()

            lat_raw = row.get("Lateralidade", "").strip()
            lat_choices = {c.value for c in Lateralidade}
            if lat_raw in lat_choices:
                lateralidade = lat_raw
            else:
                seg_lower = segmento.lower()
                lateralidade = (
                    Lateralidade.NAO_E_O_CASO
                    if seg_lower in {"coluna", "core", "bacia", "tórax", "torax"}
                    else Lateralidade.BILATERAL
                )

            causa_raw = row.get("Causa", "").strip()
            classificacao_atividade = _CAUSA_MAP.get(causa_raw, causa_raw)
            tipo_atividade = row.get("Atividade", "").strip()
            tfm_taf_val = row.get("TFM/TAF", "").strip()
            modalidade = row.get("Modalidade", "").strip()
            conduta_raw = row.get("Tratamento", "").strip()
            conduta = _CONDUTA_MAP.get(conduta_raw, conduta_raw)

            flag_sred = tipo_lesao == TipoLesao.OSSEA and origem_normalizada == OrigemLesao.POR_ESTRESSE
            sred_raw = row.get("S-RED", "").strip()
            decisao_sred = _SRED_MAP.get(sred_raw, DecisaoSred.POSITIVO) if flag_sred else ""

            exames = [col for col in _EXAMES_COLS if row.get(col, "").strip().upper() == "X"]
            encaminhamentos = [
                label for col, label in _ENC_MAP.items() if row.get(col, "").strip().upper() == "X"
            ]
            disposicao_list = [
                label for col, label in _DISP_MAP.items() if row.get(col, "").strip().upper() == "X"
            ]
            medicamentoso = row.get("Medicamentoso", "").strip().lower() == "sim"

            ref = None
            if tipo_lesao and segmento and (localizacao or estrutura):
                ref, _ = SaudeReferenciaLesao.objects.get_or_create(
                    tipo_tecido=tipo_lesao,
                    regiao_geral=segmento,
                    sub_regiao=estrutura or localizacao,
                    item_especifico=localizacao or estrutura,
                )

            atendimentos.append(Atendimento(
                data_registro=dt,
                cadete=cadete,
                medico=medico,
                tipo_atendimento=tipo_atend,
                tipo_lesao=tipo_lesao,
                origem_lesao=origem_normalizada,
                segmento_corporal=segmento,
                estrutura_anatomica=estrutura,
                localizacao_lesao=localizacao,
                lateralidade=lateralidade,
                referencia_lesao=ref,
                classificacao_atividade=classificacao_atividade,
                tipo_atividade=tipo_atividade,
                tfm_taf=tfm_taf_val,
                modalidade_esportiva=modalidade,
                conduta_terapeutica=conduta,
                decisao_sred=decisao_sred,
                medicamentoso=medicamentoso,
                solicitar_exames_complementares=len(exames) > 0,
                exames_complementares=exames,
                encaminhamentos_multidisciplinares=encaminhamentos,
                disposicao_cadete=disposicao_list,
                notas_clinicas="Tratamento medicamentoso prescrito." if medicamentoso else "",
                flag_sred=flag_sred,
            ))

        field = Atendimento._meta.get_field("data_registro")
        original_auto = field.auto_now_add
        field.auto_now_add = False
        try:
            created = Atendimento.objects.bulk_create(atendimentos)
        finally:
            field.auto_now_add = original_auto

        return Response({
            "criados": len(created),
            "cadetes_novos": cadete_counter,
            "avisos": avisos[:50],
        }, status=status.HTTP_201_CREATED)
