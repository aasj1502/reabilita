from datetime import datetime, time

from django.db.models import CharField, Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pessoal.models import Militar
from apps.saude.models import Atendimento, EvolucaoMultidisciplinar

from .permissions import IsEquipeSaudeOuStaff
from .serializers import PainelClinicoSerializer


class SredAnualView(APIView):
    permission_classes = [IsAuthenticated, IsEquipeSaudeOuStaff]

    def get(self, request):
        return Response({"items": []})


class EficaciaReabilitacaoView(APIView):
    permission_classes = [IsAuthenticated, IsEquipeSaudeOuStaff]

    def get(self, request):
        return Response({"percentual_lesoes_sem_retorno_preveniveis": 0.0})


class PainelClinicoView(APIView):
    permission_classes = [IsAuthenticated, IsEquipeSaudeOuStaff]

    @staticmethod
    def _shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
        month_index = (year * 12 + (month - 1)) + delta
        shifted_year, shifted_month_index = divmod(month_index, 12)
        return shifted_year, shifted_month_index + 1

    @staticmethod
    def _mapear_perfil(perfil_raw: str) -> str | None:
        perfil = (perfil_raw or "").strip().lower()

        if perfil == "médico":
            return "Médico"
        if perfil == "fisioterapeuta":
            return "Fisioterapeuta"
        if perfil in {"ed. físico", "educador físico", "educador fisico", "ed fisico"}:
            return "Ed. Físico"
        if perfil == "nutricionista":
            return "Nutricionista"
        if perfil == "psicopedagogo":
            return "Psicopedagogo"

        return None

    def get(self, request):
        hoje = timezone.localdate()
        total_cadetes = Militar.objects.count()
        total_atendimentos = Atendimento.objects.count()
        atendimentos_por_data = Atendimento.objects.filter(data_registro__date=hoje).count()
        cadetes_com_atendimento = Atendimento.objects.values("cadete_id").distinct().count()
        total_retornos = max(total_atendimentos - cadetes_com_atendimento, 0)

        ano_inicio, mes_inicio = self._shift_month(hoje.year, hoje.month, -5)
        inicio_data = datetime(ano_inicio, mes_inicio, 1).date()
        inicio_periodo = timezone.make_aware(datetime.combine(inicio_data, time.min))

        meses_base: dict[str, dict[str, int | str]] = {}
        for i in range(5, -1, -1):
            ano_mes, mes_mes = self._shift_month(hoje.year, hoje.month, -i)
            chave = f"{ano_mes:04d}-{mes_mes:02d}"
            meses_base[chave] = {
                "mes": f"{mes_mes:02d}/{ano_mes}",
                "total": 0,
            }

        atendimentos_por_mes = (
            Atendimento.objects.filter(data_registro__gte=inicio_periodo)
            .annotate(mes_ref=TruncMonth("data_registro"))
            .values("mes_ref")
            .annotate(total=Count("id"))
            .order_by("mes_ref")
        )

        for item in atendimentos_por_mes:
            mes_ref = item.get("mes_ref")
            if not mes_ref:
                continue
            chave = f"{mes_ref.year:04d}-{mes_ref.month:02d}"
            if chave not in meses_base:
                continue
            meses_base[chave]["total"] = int(item.get("total", 0))

        perfis_base = {
            "Médico": 0,
            "Fisioterapeuta": 0,
            "Ed. Físico": 0,
            "Nutricionista": 0,
            "Psicopedagogo": 0,
        }

        encaminhamentos_raw = (
            EvolucaoMultidisciplinar.objects.values("profissional__especialidade")
            .annotate(total=Count("id"))
            .order_by("profissional__especialidade")
        )

        for item in encaminhamentos_raw:
            perfil_normalizado = self._mapear_perfil(item.get("profissional__especialidade", ""))
            if not perfil_normalizado:
                continue
            perfis_base[perfil_normalizado] += int(item.get("total", 0))

        total_encaminhamentos = sum(perfis_base.values())
        encaminhamentos_por_perfil = [
            {
                "perfil": perfil,
                "percentual": round((total / total_encaminhamentos) * 100, 1)
                if total_encaminhamentos > 0
                else 0.0,
                "total": total,
            }
            for perfil, total in perfis_base.items()
        ]

        conduta_subquery = Subquery(
            EvolucaoMultidisciplinar.objects.filter(atendimento_id=OuterRef("pk"))
            .order_by("-data_evolucao")
            .values("parecer_tecnico")[:1],
            output_field=CharField(),
        )

        ultimos_atendimentos_qs = (
            Atendimento.objects.select_related("cadete")
            .annotate(
                conduta_atual=Coalesce(
                    conduta_subquery,
                    Value("Sem conduta registrada"),
                    output_field=CharField(),
                )
            )
            .order_by("-data_registro")[:8]
        )

        ultimos_atendimentos = [
            {
                "cadete": item.cadete.nome_completo,
                "data": item.data_registro,
                "tipo": item.tipo_lesao,
                "lesao": item.estrutura_anatomica,
                "conduta": item.conduta_atual,
            }
            for item in ultimos_atendimentos_qs
        ]

        payload = {
            "metricas": {
                "cadetes": total_cadetes,
                "atendimentos": total_atendimentos,
                "por_data": atendimentos_por_data,
                "retornos": total_retornos,
            },
            "atendimentos_ultimos_6_meses": list(meses_base.values()),
            "encaminhamentos_por_perfil": encaminhamentos_por_perfil,
            "ultimos_atendimentos": ultimos_atendimentos,
        }

        serializer = PainelClinicoSerializer(payload)
        return Response(serializer.data)
