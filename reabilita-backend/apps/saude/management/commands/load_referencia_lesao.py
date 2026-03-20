"""Management command: popula SaudeReferenciaLesao a partir de analise_mapeamento_consolidado.csv.

Padrão do CSV (3 colunas): coluna_csv, item_detalhado, tipo_tecido
Hierarquia por grupo (linhas que compartilham o mesmo coluna_csv):
  1ª linha → regiao_geral  (ex.: Membros Superiores, Coluna, Bacia)
  2ª linha → sub_regiao     (ex.: Ombro, Braço, Cervical)
  3ª+ linhas → item_especifico (ex.: Clavícula, Úmero proximal)
"""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.saude.models import SaudeReferenciaLesao

ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
FILE_NAME = "analise_mapeamento_consolidado.csv"


def _read_text(file_path: Path) -> str:
    for encoding in ENCODINGS:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(encoding="latin-1", errors="ignore")


def _parse_csv(file_path: Path) -> list[dict[str, str]]:
    """Lê o CSV e retorna registros prontos para SaudeReferenciaLesao."""
    text = _read_text(file_path)
    reader = csv.DictReader(io.StringIO(text))
    # Agrupa linhas por coluna_csv mantendo a ordem de inserção
    groups: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in reader:
        coluna = (row.get("coluna_csv") or "").strip()
        item = (row.get("item_detalhado") or "").strip()
        tipo = (row.get("tipo_tecido") or "").strip()
        if coluna and item and tipo:
            groups[coluna].append((item, tipo))

    registros: list[dict[str, str]] = []
    for _coluna, rows in groups.items():
        if len(rows) < 2:
            continue

        tipo_tecido = rows[0][1]
        regiao_geral = rows[0][0]
        sub_regiao = rows[1][0]

        if len(rows) == 2:
            # Apenas regiao + sub_regiao, sem itens específicos
            registros.append(
                {
                    "tipo_tecido": tipo_tecido,
                    "regiao_geral": regiao_geral,
                    "sub_regiao": sub_regiao,
                    "item_especifico": sub_regiao,
                }
            )
        else:
            for item, _tipo in rows[2:]:
                registros.append(
                    {
                        "tipo_tecido": tipo_tecido,
                        "regiao_geral": regiao_geral,
                        "sub_regiao": sub_regiao,
                        "item_especifico": item,
                    }
                )

    return registros


class Command(BaseCommand):
    help = "Popula SaudeReferenciaLesao a partir de analise_mapeamento_consolidado.csv."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove todos os registros antes de recarregar.",
        )

    def handle(self, *args, **options):
        data_dir = Path(settings.BASE_DIR) / "dados"
        csv_path = data_dir / FILE_NAME

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"Arquivo não encontrado: {csv_path}"))
            return

        registros = _parse_csv(csv_path)
        self.stdout.write(f"Registros extraídos do CSV: {len(registros)}")

        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            if options.get("reset"):
                deleted, _ = SaudeReferenciaLesao.objects.all().delete()
                self.stdout.write(self.style.WARNING(f"Reset: {deleted} registros removidos."))

            for reg in registros:
                _obj, created = SaudeReferenciaLesao.objects.get_or_create(
                    tipo_tecido=reg["tipo_tecido"],
                    regiao_geral=reg["regiao_geral"],
                    sub_regiao=reg["sub_regiao"],
                    item_especifico=reg["item_especifico"],
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Concluído: {created_count} criados, {skipped_count} já existentes (ignorados)."
            )
        )
