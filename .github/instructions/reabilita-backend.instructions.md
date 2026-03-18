---
description: "Use when editing Python, Django, DRF, PostgreSQL modeling, CSV mapping docs, or data rules in reabilita-backend. Enforce medical lock, S-RED trigger, laterality, and oncologic consistency."
name: "Reabilita Backend Instructions"
applyTo: "reabilita-backend/**/*.py, reabilita-backend/dados/**/*.md, reabilita-backend/dados/**/*.csv"
---

# Backend Instructions — Reabilita

- Organize by domain modules whenever new backend code is created: apps, models, serializers, views, permissions.
- Treat serializer output as the API contract and keep naming/enums synchronized with frontend types.
- Enforce permissions in backend before splitting flows by profile (Médico, Instrutor, and others).
- Mandatory domain rules:
  - Medical lock: block saving atendimento without valid `medico_id`.
  - S-RED trigger: Óssea + Por Estresse, or CID-10 `M84.3`, must set `flag_sred = true` and activate multidisciplinary protocol.
  - Laterality: Direita/Esquerda/Bilateral for limbs; “Não é o caso” for midline structures.
  - Oncologic consistency: bone CID-O morphologies (for example `M9180/3`) must be compatible with CID-10 `C40-C41`.
- Preserve source-data fidelity from provided CSV files; avoid ad-hoc code values outside official datasets.
- For critical safeguards, prefer DB constraints and backend validation/signals in addition to any UI checks.
- Document mapping decisions and ETL/data-flow changes in Markdown under `reabilita-backend/dados/`.
