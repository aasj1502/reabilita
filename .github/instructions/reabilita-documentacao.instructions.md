---
description: "Use when editing domain documentation in Markdown under reabilita-frontend/fontes or reabilita-backend/dados. Enforce technical traceability, clinical consistency, and alignment with mandatory Reabilita business rules."
name: "Reabilita Domain Documentation Instructions"
applyTo: "reabilita-frontend/fontes/**/*.md, reabilita-backend/dados/**/*.md"
---

# Domain Documentation Instructions — Reabilita

- Write in clear technical Portuguese with objective structure and explicit section titles.
- Keep documentation aligned with the current repository state; do not describe implemented services or commands that do not exist yet.
- Use source-of-truth references already present in the repository and keep terminology consistent across documents.

## Mandatory business-rule consistency

- Preserve and explicitly respect these rules whenever examples, data flow, or validations are documented:
  - Trava Médica: atendimento cannot be saved without valid `medico_id`.
  - Gatilho S-RED: Óssea + Por Estresse (or CID-10 `M84.3`) activates `flag_sred` and multidisciplinary protocol.
  - Lateralidade: Direita/Esquerda/Bilateral for limbs; “Não é o caso” for midline structures.
  - Consistência oncológica: CID-O bone morphologies (for example `M9180/3`) compatible with CID-10 `C40-C41`.

## Traceability and data-fidelity rules

- Do not invent clinical mappings or ranges. Keep mappings traceable to repository sources (CSV and model documents).
- When changing one mapping rule, update dependent documentation sections to avoid contradictions.
- Use normalized naming for entities and fields (for example `tipo_lesao`, `lateralidade`, `codigo_cid10`, `codigo_cido`, `flag_sred`).
- Distinguish clearly between:
  - current implementation state,
  - target architecture,
  - proposed future work.

## Authoring style

- Prefer compact sections with bullet points and deterministic wording.
- Avoid ambiguous language for critical validations and governance rules.
- Keep examples minimal and representative; avoid long hypothetical scenarios.
- If uncertainty exists, state assumptions explicitly instead of implying certainty.
