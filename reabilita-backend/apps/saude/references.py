from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import importlib
from pathlib import Path
from typing import Iterable

from django.conf import settings

from .models import Lateralidade, SacMapeamento, TipoLesao

TIPO_ATENDIMENTO_OPTIONS = ["Inicial", "Retorno"]
ENCAMINHAMENTOS_OPTIONS = [
    "Fisioterapia",
    "Educador Físico",
    "Nutricionista",
    "Psicopedagogo",
]
DISPOSICAO_OPTIONS = ["Dispensado", "Regime Limitado", "Alta", "Risco Cirúrgico", "VCL"]
EXAMES_COMPLEMENTARES_OPTIONS = ["RX", "USG", "TC", "RM", "DEXA", "Sangue"]
DECISAO_SRED_OPTIONS = ["S-RED Positivo", "S-RED Negativo"]

DEFAULT_CLASSIFICACAO_ATIVIDADE_OPTIONS = [
    "Não informado",
    "Evitável",
    "Relacionado à Atividade",
]
DEFAULT_TIPO_ATIVIDADE_OPTIONS = ["Não informado"]
DEFAULT_TFM_TAF_OPTIONS = ["Não informado"]
DEFAULT_MODALIDADE_ESPORTIVA_OPTIONS = ["Não informado"]
DEFAULT_CONDUTA_TERAPEUTICA_OPTIONS = [
    "Não definido",
    "Cirurgico",
    "Conservador",
    "Pós-operatório",
    "Aguardando Exame",
]

FALLBACK_ATIVIDADE_OPTIONS = [
    "Acadêmicas",
    "Campo",
    "Deslocamento",
    "EDL",
    "Equitação",
    "Formatura",
    "Inopinado",
    "Manobrão",
    "Marcha",
    "NAVAMAER",
    "Outros",
    "Parque",
    "Serviço",
    "SIESP",
    "TFM/TAF",
    "Treino atleta",
]

FALLBACK_TFM_TAF_OPTIONS = [
    "Abdominal",
    "Barra",
    "Corda",
    "Corrida",
    "Flexão",
    "Natação",
    "Pista Rondom",
    "PPM",
    "Salto plataforma",
]

FALLBACK_MODALIDADE_ESPORTIVA_OPTIONS = [
    "Aquathlon",
    "Atletismo",
    "Basquetebol",
    "Esgrima",
    "Futebol",
    "Hipismo",
    "Judô",
    "Natação",
    "Orientação",
    "Pentatlo Militar",
    "Pentatlo Moderno",
    "Polo Aquático",
    "Tiro",
    "Triatlo",
    "Voleibol",
]

TIPO_LESAO_TO_PARTE_FIELD = {
    TipoLesao.OSSEA: "parte_corpo_ossea_articular",
    TipoLesao.ARTICULAR: "parte_corpo_ossea_articular",
    TipoLesao.MUSCULAR: "parte_corpo_muscular",
    TipoLesao.TENDINOSA: "parte_corpo_tendinosa",
    TipoLesao.NEUROLOGICA: "parte_corpo_neurologica",
}

SEGMENTO_TO_ESTRUTURA_FIELD = {
    "membros superiores": "membros_superiores",
    "membros inferiores": "membros_inferiores",
    "coluna": "coluna",
    "bacia": "bacia",
    "tórax": "coluna",
    "torax": "coluna",
    "core": "coluna",
}


MIDLINE_SEGMENTOS = {"coluna", "bacia", "tórax", "torax", "core"}


def _normalize_text(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _ordered(values: Iterable[str]) -> list[str]:
    return sorted({value.strip() for value in values if value and value.strip()}, key=_normalize_text)


def _unique_preserve_order(values: Iterable[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()

    for value in values:
        text = (value or "").strip()
        if not text:
            continue
        normalized = _normalize_text(text)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(text)

    return unique


def segmento_to_estrutura_field(segmento: str | None) -> str | None:
    normalized = _normalize_text(segmento)
    return SEGMENTO_TO_ESTRUTURA_FIELD.get(normalized)


def infer_lateralidade(segmento: str | None, estrutura: str | None, lateralidade_raw: str | None) -> str:
    raw = (lateralidade_raw or "").strip()
    if raw in {
        Lateralidade.DIREITA,
        Lateralidade.ESQUERDA,
        Lateralidade.BILATERAL,
        Lateralidade.NAO_E_O_CASO,
    }:
        return raw

    estrutura_normalizada = _normalize_text(estrutura)
    segmento_normalizado = _normalize_text(segmento)

    if "direit" in estrutura_normalizada:
        return Lateralidade.DIREITA
    if "esquerd" in estrutura_normalizada:
        return Lateralidade.ESQUERDA
    if segmento_normalizado in MIDLINE_SEGMENTOS:
        return Lateralidade.NAO_E_O_CASO
    return Lateralidade.BILATERAL


def build_sac_reference_maps(rows: Iterable[SacMapeamento] | None = None) -> dict[str, object]:
    sac_rows = list(rows) if rows is not None else list(SacMapeamento.objects.order_by("id"))

    segmentos_por_tipo_lesao: dict[str, list[str]] = {}
    estruturas_por_tipo_segmento: dict[str, dict[str, list[str]]] = {}
    localizacoes_por_tipo_segmento: dict[str, dict[str, list[str]]] = {}
    lateralidade_por_estrutura: dict[str, str] = {}

    for tipo_lesao, parte_field in TIPO_LESAO_TO_PARTE_FIELD.items():
        segmentos = set()
        estruturas_map: dict[str, set[str]] = defaultdict(set)
        localizacoes_map: dict[str, set[str]] = defaultdict(set)

        for row in sac_rows:
            segmento = (getattr(row, parte_field, "") or "").strip()
            if not segmento:
                continue

            segmentos.add(segmento)
            estrutura_field = segmento_to_estrutura_field(segmento)
            if not estrutura_field:
                continue

            estrutura = (getattr(row, estrutura_field, "") or "").strip()
            if not estrutura:
                continue

            estruturas_map[segmento].add(estrutura)
            localizacoes_map[segmento].add(estrutura)

            lateralidade = infer_lateralidade(segmento, estrutura, getattr(row, "lateralidade", ""))
            if estrutura not in lateralidade_por_estrutura:
                lateralidade_por_estrutura[estrutura] = lateralidade

        segmentos_ordenados = _ordered(segmentos)
        segmentos_por_tipo_lesao[tipo_lesao] = segmentos_ordenados

        estruturas_por_tipo_segmento[tipo_lesao] = {
            segmento: _ordered(estruturas_map.get(segmento, set()))
            for segmento in segmentos_ordenados
        }

        localizacoes_por_tipo_segmento[tipo_lesao] = {
            segmento: _ordered(localizacoes_map.get(segmento, set()))
            for segmento in segmentos_ordenados
        }

    return {
        "segmentos_por_tipo_lesao": segmentos_por_tipo_lesao,
        "estruturas_por_tipo_segmento": estruturas_por_tipo_segmento,
        "localizacoes_por_tipo_segmento": localizacoes_por_tipo_segmento,
        "lateralidade_por_estrutura": lateralidade_por_estrutura,
    }


def _extract_options_from_raw_data(
    rows: Iterable[SacMapeamento],
    key_tokens: tuple[str, ...],
    fallback: list[str],
) -> list[str]:
    values: list[str] = []

    for row in rows:
        raw_data = getattr(row, "raw_data", None) or {}
        for key, raw_value in raw_data.items():
            key_normalized = _normalize_text(str(key))
            if not any(token in key_normalized for token in key_tokens):
                continue

            value = str(raw_value or "").strip()
            if value:
                values.append(value)

    unique_values = _unique_preserve_order(values)
    if unique_values:
        return unique_values
    return list(fallback)


@lru_cache(maxsize=1)
def _load_atividade_options_from_xlsx() -> dict[str, list[str]]:
    sac_file = Path(settings.BASE_DIR) / "dados" / "sac.xlsx"
    if not sac_file.exists():
        return {}

    try:
        openpyxl_module = importlib.import_module("openpyxl")
        load_workbook = getattr(openpyxl_module, "load_workbook")
    except Exception:
        return {}

    workbook = None
    try:
        workbook = load_workbook(sac_file, data_only=True, read_only=True)
        if "Atividade" not in workbook.sheetnames:
            return {}

        worksheet = workbook["Atividade"]
        row_iter = worksheet.iter_rows(min_row=1, values_only=True)
        header = next(row_iter, None)
        if not header:
            return {}

        header_index = {
            _normalize_text(str(value or "")): index
            for index, value in enumerate(header)
            if _normalize_text(str(value or ""))
        }

        atividade_idx = header_index.get("atividade")
        tfm_taf_idx = header_index.get("tfm_taf")
        modalidade_idx = header_index.get("modalidade")

        atividade_values: list[str] = []
        tfm_taf_values: list[str] = []
        modalidade_values: list[str] = []

        for row in row_iter:
            if atividade_idx is not None and atividade_idx < len(row):
                value = str(row[atividade_idx] or "").strip()
                if value:
                    atividade_values.append(value)

            if tfm_taf_idx is not None and tfm_taf_idx < len(row):
                value = str(row[tfm_taf_idx] or "").strip()
                if value:
                    tfm_taf_values.append(value)

            if modalidade_idx is not None and modalidade_idx < len(row):
                value = str(row[modalidade_idx] or "").strip()
                if value:
                    modalidade_values.append(value)

        return {
            "classificacao_atividade_options": _unique_preserve_order(atividade_values),
            "tipo_atividade_options": _unique_preserve_order(atividade_values),
            "tfm_taf_options": _unique_preserve_order(tfm_taf_values),
            "modalidade_esportiva_options": _unique_preserve_order(modalidade_values),
        }
    except Exception:
        return {}
    finally:
        if workbook is not None:
            workbook.close()


def build_atividade_contexto_options(rows: Iterable[SacMapeamento] | None = None) -> dict[str, list[str]]:
    sac_rows = list(rows) if rows is not None else list(SacMapeamento.objects.order_by("id"))

    from_xlsx = _load_atividade_options_from_xlsx()

    tipo_atividade_raw = _extract_options_from_raw_data(
        sac_rows,
        ("tipo_atividade", "atividade_tipo", "atividade"),
        [],
    )
    tfm_taf_raw = _extract_options_from_raw_data(
        sac_rows,
        ("tfm", "taf", "tfm_taf", "tfm/taf"),
        [],
    )
    modalidade_raw = _extract_options_from_raw_data(
        sac_rows,
        ("modalidade", "modalidade_esportiva"),
        [],
    )
    conduta_raw = _extract_options_from_raw_data(
        sac_rows,
        ("conduta", "conduta_terapeutica"),
        [],
    )

    classificacao_options = list(DEFAULT_CLASSIFICACAO_ATIVIDADE_OPTIONS)

    tipo_atividade_options = _unique_preserve_order(
        [
            *DEFAULT_TIPO_ATIVIDADE_OPTIONS,
            *from_xlsx.get("tipo_atividade_options", []),
            *tipo_atividade_raw,
        ]
    )
    if tipo_atividade_options == list(DEFAULT_TIPO_ATIVIDADE_OPTIONS):
        tipo_atividade_options = _unique_preserve_order(
            [
                *DEFAULT_TIPO_ATIVIDADE_OPTIONS,
                *FALLBACK_ATIVIDADE_OPTIONS,
            ]
        )

    tfm_taf_options = _unique_preserve_order(
        [
            *DEFAULT_TFM_TAF_OPTIONS,
            *from_xlsx.get("tfm_taf_options", []),
            *tfm_taf_raw,
        ]
    )
    if tfm_taf_options == list(DEFAULT_TFM_TAF_OPTIONS):
        tfm_taf_options = _unique_preserve_order(
            [
                *DEFAULT_TFM_TAF_OPTIONS,
                *FALLBACK_TFM_TAF_OPTIONS,
            ]
        )

    modalidade_options = _unique_preserve_order(
        [
            *DEFAULT_MODALIDADE_ESPORTIVA_OPTIONS,
            *from_xlsx.get("modalidade_esportiva_options", []),
            *modalidade_raw,
        ]
    )
    if modalidade_options == list(DEFAULT_MODALIDADE_ESPORTIVA_OPTIONS):
        modalidade_options = _unique_preserve_order(
            [
                *DEFAULT_MODALIDADE_ESPORTIVA_OPTIONS,
                *FALLBACK_MODALIDADE_ESPORTIVA_OPTIONS,
            ]
        )

    conduta_options = _unique_preserve_order(
        [
            *DEFAULT_CONDUTA_TERAPEUTICA_OPTIONS,
            *conduta_raw,
        ]
    )
    if not conduta_options:
        conduta_options = list(DEFAULT_CONDUTA_TERAPEUTICA_OPTIONS)

    return {
        "classificacao_atividade_options": classificacao_options or list(DEFAULT_CLASSIFICACAO_ATIVIDADE_OPTIONS),
        "tipo_atividade_options": tipo_atividade_options or list(DEFAULT_TIPO_ATIVIDADE_OPTIONS),
        "tfm_taf_options": tfm_taf_options or list(DEFAULT_TFM_TAF_OPTIONS),
        "modalidade_esportiva_options": modalidade_options or list(DEFAULT_MODALIDADE_ESPORTIVA_OPTIONS),
        "conduta_terapeutica_options": conduta_options,
    }
