from __future__ import annotations

import csv
import io
import json
import unicodedata
from hashlib import sha256
from pathlib import Path

from django.conf import settings
from django.db import transaction

from ..models import (
    CargaReferenciaHistorico,
    CargaStatus,
    Cid10Categoria,
    CidOMorfologia,
    RecordChangeAudit,
    ReferenciaArquivoVersao,
    SacMapeamento,
)

ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
FILE_NAME_CID10 = "CID-10-CATEGORIAS.CSV"
FILE_NAME_CIDO = "CID-O-CATEGORIAS.CSV"
FILE_NAME_SAC = "sac_convertido.csv"


def _read_text(file_path: Path) -> str:
    for encoding in ENCODINGS:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(encoding="latin-1", errors="ignore")


def _compute_checksum(file_path: Path) -> str:
    return sha256(file_path.read_bytes()).hexdigest()


def _normalize_key(value: str | None) -> str:
    text = (value or "").strip()
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    lowered = without_accents.lower()
    cleaned = []
    for char in lowered:
        cleaned.append(char if char.isalnum() else "_")
    return "".join(cleaned).strip("_")


def _compute_record_hash(data: dict[str, str]) -> str:
    """Computa SHA-256 de um registro (ex: linha de CSV)."""
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()


def _detect_changes(old_data: dict[str, str], new_data: dict[str, str]) -> dict[str, list]:
    """Detecta campos alterados entre duas versões de um registro."""
    changed = {}
    all_keys = set(old_data.keys()) | set(new_data.keys())
    for key in all_keys:
        old_val = old_data.get(key, "")
        new_val = new_data.get(key, "")
        if old_val != new_val:
            changed[key] = [old_val, new_val]
    return changed


def _pk_value(instance: object) -> int:
    pk = getattr(instance, "pk", 0)
    if pk is None:
        return 0
    return int(pk)


def _clean_row(row: dict[str, str]) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    for key, value in row.items():
        normalized_key = _normalize_key(key)
        if not normalized_key:
            continue
        cleaned[normalized_key] = (value or "").strip()
    return cleaned


def _read_semicolon_dict_rows(file_path: Path) -> list[dict[str, str]]:
    text = _read_text(file_path)
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows: list[dict[str, str]] = []
    for raw in reader:
        cleaned = _clean_row(raw)
        if any(cleaned.values()):
            rows.append(cleaned)
    return rows


def _read_sac_rows(file_path: Path) -> list[dict[str, str]]:
    text = _read_text(file_path)
    reader = csv.reader(io.StringIO(text), delimiter=";")
    rows = [row for row in reader if any((cell or "").strip() for cell in row)]

    if not rows:
        return []

    header_row = rows[0]
    data_rows = rows[1:]

    if len(rows) >= 2 and any("unnamed" in (cell or "").lower() for cell in rows[0]):
        header_row = rows[1]
        data_rows = rows[2:]

    headers = [_normalize_key(cell) for cell in header_row]
    parsed: list[dict[str, str]] = []

    for row in data_rows:
        normalized_row: dict[str, str] = {}
        for index, header in enumerate(headers):
            if not header:
                continue
            value = row[index] if index < len(row) else ""
            normalized_row[header] = (value or "").strip()
        if any(normalized_row.values()):
            parsed.append(normalized_row)

    return parsed


def _extract_comportamento(codigo: str) -> str:
    if "/" not in codigo:
        return ""
    return f"/{codigo.split('/', maxsplit=1)[1]}"


def _upsert_cid10_with_audit(
    rows: list[dict[str, str]],
    historico: CargaReferenciaHistorico,
) -> dict[str, int]:
    """Faz upsert de CID-10 com detecção de mudanças por linha."""
    created = 0
    updated = 0
    unchanged = 0

    for row in rows:
        codigo = row.get("cat", "").upper()
        if not codigo:
            continue

        record_hash = _compute_record_hash(row)
        data_dict = {
            "codigo": codigo,
            "classificacao": row.get("classif", ""),
            "descricao": row.get("descricao", ""),
            "descricao_abreviada": row.get("descrabrev", ""),
            "referencia": row.get("refer", ""),
            "excluidos": row.get("excluidos", ""),
        }

        existing = Cid10Categoria.objects.filter(codigo=codigo).first()

        if existing is None:
            obj = Cid10Categoria(
                record_hash=record_hash,
                raw_data=row,
                **data_dict,
            )
            obj.save()
            RecordChangeAudit.objects.create(
                tabela="Cid10Categoria",
                registro_id=_pk_value(obj),
                chave_registra=codigo,
                tipo_mudanca=RecordChangeAudit.ChangeType.CREATED,
                hash_novo=record_hash,
                historico_carga=historico,
            )
            created += 1
        elif existing.record_hash != record_hash:
            hash_anterior = existing.record_hash
            old_data = {k: getattr(existing, k, "") or "" for k in data_dict.keys()}
            changes = _detect_changes(old_data, data_dict)

            for key, value in data_dict.items():
                setattr(existing, key, value)
            existing.record_hash = record_hash
            existing.raw_data = row
            existing.save()

            RecordChangeAudit.objects.create(
                tabela="Cid10Categoria",
                registro_id=_pk_value(existing),
                chave_registra=codigo,
                tipo_mudanca=RecordChangeAudit.ChangeType.UPDATED,
                hash_anterior=hash_anterior,
                hash_novo=record_hash,
                dados_alterados=changes,
                historico_carga=historico,
            )
            updated += 1
        else:
            RecordChangeAudit.objects.create(
                tabela="Cid10Categoria",
                registro_id=_pk_value(existing),
                chave_registra=codigo,
                tipo_mudanca=RecordChangeAudit.ChangeType.UNCHANGED,
                hash_novo=record_hash,
                historico_carga=historico,
            )
            unchanged += 1

    return {"created": created, "updated": updated, "unchanged": unchanged}


def _upsert_cido_with_audit(
    rows: list[dict[str, str]],
    historico: CargaReferenciaHistorico,
) -> dict[str, int]:
    """Faz upsert de CID-O com detecção de mudanças por linha."""
    created = 0
    updated = 0
    unchanged = 0

    for row in rows:
        codigo = row.get("cat", "").upper()
        if not codigo:
            continue

        record_hash = _compute_record_hash(row)
        data_dict = {
            "codigo": codigo,
            "descricao": row.get("descricao", ""),
            "referencia": row.get("refer", ""),
            "comportamento": _extract_comportamento(codigo),
        }

        existing = CidOMorfologia.objects.filter(codigo=codigo).first()

        if existing is None:
            obj = CidOMorfologia(
                record_hash=record_hash,
                raw_data=row,
                **data_dict,
            )
            obj.save()
            RecordChangeAudit.objects.create(
                tabela="CidOMorfologia",
                registro_id=_pk_value(obj),
                chave_registra=codigo,
                tipo_mudanca=RecordChangeAudit.ChangeType.CREATED,
                hash_novo=record_hash,
                historico_carga=historico,
            )
            created += 1
        elif existing.record_hash != record_hash:
            hash_anterior = existing.record_hash
            old_data = {k: getattr(existing, k, "") or "" for k in data_dict.keys()}
            changes = _detect_changes(old_data, data_dict)

            for key, value in data_dict.items():
                setattr(existing, key, value)
            existing.record_hash = record_hash
            existing.raw_data = row
            existing.save()

            RecordChangeAudit.objects.create(
                tabela="CidOMorfologia",
                registro_id=_pk_value(existing),
                chave_registra=codigo,
                tipo_mudanca=RecordChangeAudit.ChangeType.UPDATED,
                hash_anterior=hash_anterior,
                hash_novo=record_hash,
                dados_alterados=changes,
                historico_carga=historico,
            )
            updated += 1
        else:
            RecordChangeAudit.objects.create(
                tabela="CidOMorfologia",
                registro_id=_pk_value(existing),
                chave_registra=codigo,
                tipo_mudanca=RecordChangeAudit.ChangeType.UNCHANGED,
                hash_novo=record_hash,
                historico_carga=historico,
            )
            unchanged += 1

    return {"created": created, "updated": updated, "unchanged": unchanged}


def _upsert_sac_with_audit(
    rows: list[dict[str, str]],
    historico: CargaReferenciaHistorico,
) -> dict[str, int]:
    """Faz upsert de SAC por posição de linha para preservar registros sem chave natural."""
    created = 0
    updated = 0
    unchanged = 0

    existing_rows = list(SacMapeamento.objects.order_by("id"))

    if existing_rows and len(existing_rows) != len(rows):
        SacMapeamento.objects.all().delete()
        existing_rows = []

    for index, row in enumerate(rows, start=1):
        linha_key = f"linha_{index}"

        record_hash = _compute_record_hash(row)
        data_dict = {
            "lesao": row.get("lesao", ""),
            "parte_corpo_ossea_articular": row.get("parte_corpo_ossea_e_articular", ""),
            "parte_corpo_muscular": row.get("parte_corpo_muscular", ""),
            "parte_corpo_tendinosa": row.get("parte_corpo_tendinosa", ""),
            "parte_corpo_neurologica": row.get("parte_corpo_neurologica", ""),
            "membros_superiores": row.get("membros_superiores", ""),
            "coluna": row.get("coluna", ""),
            "bacia": row.get("bacia", ""),
            "membros_inferiores": row.get("membros_inferiores", ""),
            "lateralidade": row.get("lateralidade", ""),
        }

        existing = existing_rows[index - 1] if index - 1 < len(existing_rows) else None

        if existing is None:
            obj = SacMapeamento(
                record_hash=record_hash,
                raw_data=row,
                **data_dict,
            )
            obj.save()
            RecordChangeAudit.objects.create(
                tabela="SacMapeamento",
                registro_id=_pk_value(obj),
                chave_registra=linha_key,
                tipo_mudanca=RecordChangeAudit.ChangeType.CREATED,
                hash_novo=record_hash,
                historico_carga=historico,
            )
            created += 1
        elif existing.record_hash != record_hash:
            hash_anterior = existing.record_hash
            old_data = {k: getattr(existing, k, "") or "" for k in data_dict.keys()}
            changes = _detect_changes(old_data, data_dict)

            for key, value in data_dict.items():
                setattr(existing, key, value)
            existing.record_hash = record_hash
            existing.raw_data = row
            existing.save()

            RecordChangeAudit.objects.create(
                tabela="SacMapeamento",
                registro_id=_pk_value(existing),
                chave_registra=linha_key,
                tipo_mudanca=RecordChangeAudit.ChangeType.UPDATED,
                hash_anterior=hash_anterior,
                hash_novo=record_hash,
                dados_alterados=changes,
                historico_carga=historico,
            )
            updated += 1
        else:
            RecordChangeAudit.objects.create(
                tabela="SacMapeamento",
                registro_id=_pk_value(existing),
                chave_registra=linha_key,
                tipo_mudanca=RecordChangeAudit.ChangeType.UNCHANGED,
                hash_novo=record_hash,
                historico_carga=historico,
            )
            unchanged += 1

    return {"created": created, "updated": updated, "unchanged": unchanged}


def _build_file_status(
    nome_arquivo: str,
    checksum: str,
    row_count: int,
    versao_atual: ReferenciaArquivoVersao | None,
    reset: bool,
    force: bool,
) -> dict[str, object]:
    alterado = versao_atual is None or versao_atual.checksum_sha256 != checksum
    processado = bool(reset or force or alterado)
    versao_anterior = versao_atual.versao if versao_atual else None
    versao_nova = 1 if versao_atual is None else (versao_atual.versao + 1 if alterado else versao_atual.versao)

    return {
        "arquivo": nome_arquivo,
        "checksum_anterior": versao_atual.checksum_sha256 if versao_atual else None,
        "checksum_novo": checksum,
        "linhas_lidas": row_count,
        "alterado": alterado,
        "processado": processado,
        "versao_anterior": versao_anterior,
        "versao_nova": versao_nova,
    }


def _upsert_arquivo_versao(status: dict[str, object], total_registros: int) -> None:
    nome_arquivo = str(status["arquivo"])
    checksum_novo = str(status["checksum_novo"])
    alterado = bool(status["alterado"])
    processado = bool(status["processado"])

    if not processado:
        return

    registro = ReferenciaArquivoVersao.objects.filter(nome_arquivo=nome_arquivo).first()

    if registro is None:
        ReferenciaArquivoVersao.objects.create(
            nome_arquivo=nome_arquivo,
            checksum_sha256=checksum_novo,
            versao=1,
            total_registros=total_registros,
        )
        return

    if alterado:
        registro.versao += 1
        registro.checksum_sha256 = checksum_novo

    registro.total_registros = total_registros
    registro.save()


def _register_historico(
    *,
    status: str,
    reset: bool,
    force: bool,
    arquivos_processados: list[dict[str, object]],
    arquivos_alterados: list[str],
    resumo: dict[str, object],
    mensagem: str = "",
) -> CargaReferenciaHistorico:
    return CargaReferenciaHistorico.objects.create(
        status=status,
        reset=reset,
        force=force,
        arquivos_processados=arquivos_processados,
        arquivos_alterados=arquivos_alterados,
        resumo=resumo,
        mensagem=mensagem,
    )


def load_referencias_saude(reset: bool = False, force: bool = False) -> dict[str, object]:
    data_dir = Path(settings.BASE_DIR) / "dados"

    cid10_file = data_dir / FILE_NAME_CID10
    cido_file = data_dir / FILE_NAME_CIDO
    sac_file = data_dir / FILE_NAME_SAC

    cid10_rows = _read_semicolon_dict_rows(cid10_file)
    cido_rows = _read_semicolon_dict_rows(cido_file)
    sac_rows = _read_sac_rows(sac_file)

    cid10_checksum = _compute_checksum(cid10_file)
    cido_checksum = _compute_checksum(cido_file)
    sac_checksum = _compute_checksum(sac_file)

    versoes = {
        item.nome_arquivo: item
        for item in ReferenciaArquivoVersao.objects.filter(
            nome_arquivo__in=[FILE_NAME_CID10, FILE_NAME_CIDO, FILE_NAME_SAC]
        )
    }

    status_cid10 = _build_file_status(
        FILE_NAME_CID10,
        cid10_checksum,
        len(cid10_rows),
        versoes.get(FILE_NAME_CID10),
        reset,
        force,
    )
    status_cido = _build_file_status(
        FILE_NAME_CIDO,
        cido_checksum,
        len(cido_rows),
        versoes.get(FILE_NAME_CIDO),
        reset,
        force,
    )
    status_sac = _build_file_status(
        FILE_NAME_SAC,
        sac_checksum,
        len(sac_rows),
        versoes.get(FILE_NAME_SAC),
        reset,
        force,
    )

    arquivos_processados = [status_cid10, status_cido, status_sac]
    arquivos_alterados = [
        str(item["arquivo"])
        for item in arquivos_processados
        if bool(item["alterado"])
    ]

    if not any(bool(item["processado"]) for item in arquivos_processados):
        historico = _register_historico(
            status=CargaStatus.SEM_ALTERACAO,
            reset=reset,
            force=force,
            arquivos_processados=arquivos_processados,
            arquivos_alterados=arquivos_alterados,
            resumo={
                "cid10_carregados": 0,
                "cid10_criados": 0,
                "cid10_atualizados": 0,
                "cid10_inalterados": 0,
                "cido_carregados": 0,
                "cido_criados": 0,
                "cido_atualizados": 0,
                "cido_inalterados": 0,
                "sac_carregados": 0,
                "sac_criados": 0,
                "sac_atualizados": 0,
                "sac_inalterados": 0,
                "aplicado": False,
            },
            mensagem="Nenhuma alteração de CSV detectada.",
        )
        return {
            "historico_id": getattr(historico, "pk", None),
            "status": CargaStatus.SEM_ALTERACAO,
            "reset_aplicado": reset,
            "force_aplicado": force,
            "aplicado": False,
            "arquivos_alterados": arquivos_alterados,
            "cid10_carregados": 0,
            "cido_carregados": 0,
            "sac_carregados": 0,
        }

    try:
        with transaction.atomic():
            historico = _register_historico(
                status=CargaStatus.SUCESSO,
                reset=reset,
                force=force,
                arquivos_processados=arquivos_processados,
                arquivos_alterados=arquivos_alterados,
                resumo={},
            )

            cid10_stats = {"created": 0, "updated": 0, "unchanged": 0}
            cido_stats = {"created": 0, "updated": 0, "unchanged": 0}
            sac_stats = {"created": 0, "updated": 0, "unchanged": 0}

            if bool(status_cid10["processado"]):
                if reset:
                    Cid10Categoria.objects.all().delete()
                cid10_stats = _upsert_cid10_with_audit(cid10_rows, historico)

            if bool(status_cido["processado"]):
                if reset:
                    CidOMorfologia.objects.all().delete()
                cido_stats = _upsert_cido_with_audit(cido_rows, historico)

            if bool(status_sac["processado"]):
                if reset:
                    SacMapeamento.objects.all().delete()
                sac_stats = _upsert_sac_with_audit(sac_rows, historico)

            _upsert_arquivo_versao(status_cid10, len(cid10_rows))
            _upsert_arquivo_versao(status_cido, len(cido_rows))
            _upsert_arquivo_versao(status_sac, len(sac_rows))

            resumo = {
                "cid10_carregados": len(cid10_rows),
                "cid10_criados": cid10_stats["created"],
                "cid10_atualizados": cid10_stats["updated"],
                "cid10_inalterados": cid10_stats["unchanged"],
                "cido_carregados": len(cido_rows),
                "cido_criados": cido_stats["created"],
                "cido_atualizados": cido_stats["updated"],
                "cido_inalterados": cido_stats["unchanged"],
                "sac_carregados": len(sac_rows),
                "sac_criados": sac_stats["created"],
                "sac_atualizados": sac_stats["updated"],
                "sac_inalterados": sac_stats["unchanged"],
                "aplicado": True,
            }
            historico.resumo = resumo
            historico.save()

    except Exception as exc:
        try:
            _register_historico(
                status=CargaStatus.FALHA,
                reset=reset,
                force=force,
                arquivos_processados=arquivos_processados,
                arquivos_alterados=arquivos_alterados,
                resumo={
                    "cid10_carregados": 0,
                    "cido_carregados": 0,
                    "sac_carregados": 0,
                    "aplicado": False,
                },
                mensagem=str(exc),
            )
        except Exception:
            pass
        raise

    return {
        "historico_id": getattr(historico, "pk", None),
        "status": CargaStatus.SUCESSO,
        "reset_aplicado": reset,
        "force_aplicado": force,
        "aplicado": True,
        "arquivos_alterados": arquivos_alterados,
        "cid10_carregados": resumo["cid10_carregados"],
        "cid10_criados": resumo["cid10_criados"],
        "cid10_atualizados": resumo["cid10_atualizados"],
        "cido_carregados": resumo["cido_carregados"],
        "cido_criados": resumo["cido_criados"],
        "cido_atualizados": resumo["cido_atualizados"],
        "sac_carregados": resumo["sac_carregados"],
        "sac_criados": resumo["sac_criados"],
        "sac_atualizados": resumo["sac_atualizados"],
    }
