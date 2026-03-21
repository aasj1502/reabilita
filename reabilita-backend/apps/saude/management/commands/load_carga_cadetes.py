"""
Management command para popular o banco de dados a partir de carga_cadetes.csv.

Fluxo:
1. Cria o profissional médico "1 Ten Real" (Militar + ProfissionalSaude).
2. Identifica cadetes sintéticos agrupando visitas Inicial/Retorno.
3. Cria registros de Atendimento com mapeamento completo de campos.
4. Resolve flag_sred, decisao_sred, lateralidade, exames, encaminhamentos, disposição.

Normalizações aplicadas:
- Datas: formato DD/MM/YYYY com detecção automática de inversão MM/DD.
- "Origem Traumática" → "Traumática"
- "Previnível" → "Prevenível"
- "PósOperatório" → "Pós-operatório"
- "Aguardar Exame" → "Aguardando Exame"
- S-RED: "Confirmada"→"S-RED Positivo", "Não investigar"→"S-RED Negativo",
  "Iniciar investigação"→"S-RED Positivo"
"""

import csv
from datetime import date, datetime, time, timezone
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.pessoal.models import Militar, ProfissionalSaude
from apps.saude.models import (
    Atendimento,
    DecisaoSred,
    Lateralidade,
    OrigemLesao,
    SaudeReferenciaLesao,
    TipoAtendimento,
    TipoLesao,
)

CSV_PATH = Path(__file__).resolve().parents[4] / "dados" / "carga_cadetes.csv"

# ────────────────────────── mapeamento de valores ──────────────────────────

ORIGEM_MAP = {
    "Por Estresse": OrigemLesao.POR_ESTRESSE,
    "Origem Traumática": OrigemLesao.TRAUMATICA,
}

SRED_MAP = {
    "Confirmada": DecisaoSred.POSITIVO,
    "Iniciar investigação": DecisaoSred.POSITIVO,
    "Não investigar": DecisaoSred.NEGATIVO,
}

CAUSA_MAP = {
    "Previnível": "Prevenível",
    "Decorrente da Atividade": "Decorrente da Atividade",
}

CONDUTA_MAP = {
    "Conservador": "Conservador",
    "PósOperatório": "Pós-operatório",
    "Cirúrgico": "Cirúrgico",
    "Aguardar Exame": "Aguardando Exame",
}

MIDLINE_SEGMENTOS = {"coluna", "core", "bacia", "tórax", "torax"}


# ────────────────────────── utilitários de data ──────────────────────────────

def _parse_date(text: str) -> date | None:
    """Tenta DD/MM/YYYY e, se inválido, MM/DD/YYYY."""
    text = text.strip()
    if not text:
        return None
    parts = text.split("/")
    if len(parts) != 3:
        return None
    a, b, y = int(parts[0]), int(parts[1]), int(parts[2])
    # Tenta DD/MM/YYYY
    try:
        return date(y, b, a)
    except ValueError:
        pass
    # Tenta MM/DD/YYYY
    try:
        return date(y, a, b)
    except ValueError:
        return None


def _smart_date(text: str, last_date: date | None) -> date | None:
    """Parse com preferência pelo formato que mantém ordem cronológica."""
    text = text.strip()
    if not text:
        return None
    parts = text.split("/")
    if len(parts) != 3:
        return None
    a, b, y = int(parts[0]), int(parts[1]), int(parts[2])

    candidates: list[date] = []
    # DD/MM
    try:
        candidates.append(date(y, b, a))
    except ValueError:
        pass
    # MM/DD (se ambíguo)
    if a <= 12 and b <= 31 and a != b:
        try:
            candidates.append(date(y, a, b))
        except ValueError:
            pass

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Ambíguo: preferir a que mantém ordem cronológica
    if last_date is not None:
        valid = [c for c in candidates if c >= last_date]
        if len(valid) == 1:
            return valid[0]
        if valid:
            return min(valid)

    return min(candidates)


def _parse_time(text: str) -> time:
    text = text.strip()
    if not text:
        return time(0, 0, 0)
    parts = text.split(":")
    h = int(parts[0]) if len(parts) > 0 else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    s = int(parts[2]) if len(parts) > 2 else 0
    return time(h, m, s)


def _make_datetime(d: date, t: time) -> datetime:
    return datetime.combine(d, t, tzinfo=timezone.utc)


# ────────────────────────── inferência lateralidade ──────────────────────────

def _infer_lateralidade(segmento: str, estrutura: str) -> str:
    seg = segmento.lower().strip()
    if seg in MIDLINE_SEGMENTOS:
        return Lateralidade.NAO_E_O_CASO
    return Lateralidade.BILATERAL


# ────────────────────────── resolve referencia_lesao ─────────────────────────

def _resolve_ref(tipo_lesao: str, segmento: str, estrutura: str, localizacao: str):
    if tipo_lesao and segmento and (localizacao or estrutura):
        ref, _ = SaudeReferenciaLesao.objects.get_or_create(
            tipo_tecido=tipo_lesao,
            regiao_geral=segmento,
            sub_regiao=estrutura or localizacao,
            item_especifico=localizacao or estrutura,
        )
        return ref
    return None


# ────────────────────────── command ──────────────────────────────────────────

class Command(BaseCommand):
    help = "Carrega atendimentos a partir de carga_cadetes.csv."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Apenas simula, sem gravar.")
        parser.add_argument("--clear", action="store_true", help="Remove atendimentos antes de carregar.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        clear = options["clear"]

        if clear and not dry_run:
            deleted, _ = Atendimento.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removidos {deleted} atendimentos existentes."))

        # ── Leitura do CSV ──
        if not CSV_PATH.exists():
            self.stderr.write(self.style.ERROR(f"Arquivo não encontrado: {CSV_PATH}"))
            return

        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)

        self.stdout.write(f"CSV lido: {len(rows)} linhas.")

        # ── Médico ──
        medico_mil, _ = Militar.objects.get_or_create(
            nr_militar="MED_001",
            defaults={
                "nome_completo": "1 Ten Real",
                "nome_guerra": "Real",
                "sexo": "M",
                "posto_graduacao": "1º Tenente",
            },
        )
        medico, _ = ProfissionalSaude.objects.get_or_create(
            militar=medico_mil,
            defaults={"especialidade": "Médico", "ativo": True},
        )
        self.stdout.write(f"Médico: {medico} (id={medico.pk})")

        # ── 1ª passagem: construir mapa de datas e criar cadetes ──
        # Cada Inicial gera um cadete sintético.
        # Retornos são vinculados ao cadete do Inicial correspondente.

        # Parse datas com ordem cronológica
        parsed_rows: list[dict] = []
        last_date: date | None = None

        for idx, row in enumerate(rows):
            d = _smart_date(row.get("Data", ""), last_date)
            t = _parse_time(row.get("Hora", ""))
            if d is not None:
                last_date = d
            parsed_rows.append({
                "idx": idx,
                "row": row,
                "date": d,
                "time": t,
                "dt": _make_datetime(d, t) if d else None,
            })

        # Mapa (date, time) → cadete para TODAS as visitas resolvidas
        cadete_map: dict[tuple[date, time], Militar] = {}
        cadete_counter = 0

        # 1) Criar cadetes para todos os Iniciais
        for pr in parsed_rows:
            row = pr["row"]
            tipo = row.get("Atendimento", "").strip()
            if tipo != "Inicial":
                continue
            key = (pr["date"], pr["time"])
            if key in cadete_map:
                continue
            cadete_counter += 1
            nr = f"CAD_{cadete_counter:04d}"
            sexo = row.get("Sexo", "M").strip() or "M"
            cadete, _ = Militar.objects.get_or_create(
                nr_militar=nr,
                defaults={
                    "nome_completo": f"Cadete {cadete_counter:04d}",
                    "nome_guerra": f"Cadete{cadete_counter:04d}",
                    "sexo": sexo,
                },
            )
            cadete_map[key] = cadete

        self.stdout.write(f"Cadetes criados (Iniciais): {cadete_counter}")

        # 2) Resolver Retornos iterativamente (retorno pode referenciar outro retorno)
        def _lookup_ref(dt_orig_str: str, hr_orig_str: str) -> Militar | None:
            if not dt_orig_str:
                return None
            d = _parse_date(dt_orig_str)
            t = _parse_time(hr_orig_str)
            if d and (d, t) in cadete_map:
                return cadete_map[(d, t)]
            # Tentar invertendo dia/mês
            if d and d.day <= 12 and d.month <= 12:
                swapped = date(d.year, d.day, d.month)
                if (swapped, t) in cadete_map:
                    return cadete_map[(swapped, t)]
            return None

        retorno_indices = [
            i for i, pr in enumerate(parsed_rows)
            if pr["row"].get("Atendimento", "").strip() == "Retorno"
        ]
        unresolved = set(retorno_indices)
        max_iters = 10
        for iteration in range(max_iters):
            newly_resolved = set()
            for i in list(unresolved):
                pr = parsed_rows[i]
                row = pr["row"]
                cad = _lookup_ref(
                    row.get("Dt_VisitaOrigem", "").strip(),
                    row.get("Hr_VisitaOrigem", "").strip(),
                )
                if cad is not None:
                    cadete_map[(pr["date"], pr["time"])] = cad
                    newly_resolved.add(i)
            unresolved -= newly_resolved
            if not newly_resolved:
                break

        self.stdout.write(
            f"Retornos resolvidos: {len(retorno_indices) - len(unresolved)}/{len(retorno_indices)} "
            f"({len(unresolved)} sem vínculo)"
        )

        # ── 3ª passagem: construir Atendimentos ──
        atendimentos: list[Atendimento] = []
        skipped = 0
        warnings: list[str] = []

        for pr in parsed_rows:
            row = pr["row"]
            if pr["dt"] is None:
                skipped += 1
                continue

            tipo_atend = row.get("Atendimento", "").strip()

            # Resolver cadete
            if tipo_atend == "Retorno":
                key = (pr["date"], pr["time"])
                cadete = cadete_map.get(key)
                if cadete is None:
                    # Fallback: criar cadete anônimo
                    cadete_counter += 1
                    nr = f"CAD_{cadete_counter:04d}"
                    cadete, _ = Militar.objects.get_or_create(
                        nr_militar=nr,
                        defaults={
                            "nome_completo": f"Cadete {cadete_counter:04d}",
                            "nome_guerra": f"Cadete{cadete_counter:04d}",
                            "sexo": row.get("Sexo", "M").strip() or "M",
                        },
                    )
                    warnings.append(f"Linha {pr['idx']+2}: Retorno sem Inicial — cadete {nr}")
            else:
                key = (pr["date"], pr["time"])
                cadete = cadete_map.get(key)
                if cadete is None:
                    skipped += 1
                    continue

            # Tipo de lesão
            tipo_lesao = row.get("Lesão", "").strip()
            if tipo_lesao not in {c.value for c in TipoLesao}:
                warnings.append(f"Linha {pr['idx']+2}: tipo_lesao inválido: {tipo_lesao!r}")
                skipped += 1
                continue

            # Origem da lesão
            origem_raw = row.get("Origem da Lesão", "").strip()
            origem_lesao = ORIGEM_MAP.get(origem_raw, "")

            # Segmento, estrutura, localização
            segmento = row.get("Parte do Corpo", "").strip()
            estrutura = row.get("Parte Lesionada", "").strip()
            localizacao = row.get("Local da Lesão", "").strip()

            # Lateralidade
            lat_raw = row.get("Lateralidade", "").strip()
            lat_choices = {c.value for c in Lateralidade}
            if lat_raw in lat_choices:
                lateralidade = lat_raw
            else:
                lateralidade = _infer_lateralidade(segmento, estrutura)

            # Classificação atividade (Causa)
            causa_raw = row.get("Causa", "").strip()
            classificacao_atividade = CAUSA_MAP.get(causa_raw, causa_raw)

            # Tipo atividade, TFM/TAF, modalidade
            tipo_atividade = row.get("Atividade", "").strip()
            tfm_taf = row.get("TFM/TAF", "").strip()
            modalidade = row.get("Modalidade", "").strip()

            # Conduta terapêutica
            conduta_raw = row.get("Tratamento", "").strip()
            conduta = CONDUTA_MAP.get(conduta_raw, conduta_raw)

            # S-RED / flag_sred
            sred_raw = row.get("S-RED", "").strip()
            flag_sred = (
                tipo_lesao == TipoLesao.OSSEA and origem_lesao == OrigemLesao.POR_ESTRESSE
            )
            if flag_sred:
                decisao_sred = SRED_MAP.get(sred_raw, DecisaoSred.POSITIVO)
            else:
                decisao_sred = ""

            # Exames complementares
            exames = []
            for col in ["RX", "USG", "TC", "RM", "DEXA", "Sangue"]:
                if row.get(col, "").strip().upper() == "X":
                    exames.append(col)
            solicitar_exames = len(exames) > 0

            # Encaminhamentos multidisciplinares
            encaminhamentos = []
            enc_map = {
                "Fisioterapia": "Fisioterapia",
                "SEF": "Educador Físico",
                "Nutricionista": "Nutricionista",
                "Psicopedagógica": "Psicopedagogo",
            }
            for col, label in enc_map.items():
                if row.get(col, "").strip().upper() == "X":
                    encaminhamentos.append(label)

            # Disposição do cadete
            disposicao = []
            disp_map = {
                "Dispensa": "Dispensado",
                "VCL": "VCL",
                "Alta": "Alta",
                "Risco Cirúrgico": "Risco Cirúrgico",
            }
            for col, label in disp_map.items():
                if row.get(col, "").strip().upper() == "X":
                    disposicao.append(label)

            # Notas clínicas e campo medicamentoso
            medicamentoso = row.get("Medicamentoso", "").strip().lower() == "sim"
            notas = ""
            if medicamentoso:
                notas = "Tratamento medicamentoso prescrito."

            # Referência de lesão
            ref = _resolve_ref(tipo_lesao, segmento, estrutura, localizacao)

            atendimento = Atendimento(
                data_registro=pr["dt"],
                cadete=cadete,
                medico=medico,
                tipo_atendimento=tipo_atend if tipo_atend in {"Inicial", "Retorno"} else "Inicial",
                tipo_lesao=tipo_lesao,
                origem_lesao=origem_lesao,
                segmento_corporal=segmento,
                estrutura_anatomica=estrutura,
                localizacao_lesao=localizacao,
                lateralidade=lateralidade,
                referencia_lesao=ref,
                classificacao_atividade=classificacao_atividade,
                tipo_atividade=tipo_atividade,
                tfm_taf=tfm_taf,
                modalidade_esportiva=modalidade,
                conduta_terapeutica=conduta,
                decisao_sred=decisao_sred,
                medicamentoso=medicamentoso,
                solicitar_exames_complementares=solicitar_exames,
                exames_complementares=exames,
                encaminhamentos_multidisciplinares=encaminhamentos,
                disposicao_cadete=disposicao,
                notas_clinicas=notas,
                flag_sred=flag_sred,
            )
            atendimentos.append(atendimento)

        # ── Gravar ──
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"[DRY-RUN] {len(atendimentos)} atendimentos preparados, {skipped} ignorados."
            ))
        else:
            # Desabilitar auto_now_add para preservar data_registro do CSV
            field = Atendimento._meta.get_field("data_registro")
            original = field.auto_now_add
            field.auto_now_add = False
            try:
                created = Atendimento.objects.bulk_create(atendimentos)
                self.stdout.write(self.style.SUCCESS(
                    f"Criados {len(created)} atendimentos. Ignorados: {skipped}."
                ))
            finally:
                field.auto_now_add = original

        # Avisos
        for w in warnings:
            self.stdout.write(self.style.WARNING(w))

        # Resumo
        self.stdout.write(f"\nCadetes totais: {cadete_counter}")
        self.stdout.write(f"Atendimentos carregados: {len(atendimentos)}")
        self.stdout.write(f"Linhas ignoradas: {skipped}")
        self.stdout.write(f"Avisos: {len(warnings)}")
