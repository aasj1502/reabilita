---
description: "Use when editing React, TypeScript, TSX, SCSS, design-system components, hooks, providers, or frontend API integration in reabilita-frontend. Enforce mobile-first field UX, strict DRF contract typing, and design-system-first implementation."
name: "Reabilita Frontend Instructions"
applyTo: "reabilita-frontend/src/**/*.ts, reabilita-frontend/src/**/*.tsx, reabilita-frontend/src/**/*.scss, reabilita-frontend/src/**/*.css, reabilita-frontend/fontes/**/*.md"
---

# Frontend Instructions — Reabilita

- Use only components, tokens, and providers from `reabilita-frontend/src/design-system` as UI source of truth.
- Keep types explicit. TypeScript interfaces/types must mirror Django serializer output exactly (field names, nullability, enum values).
- Prefer flow: `types` → `services` (Axios) → `hooks` (TanStack Query) → UI components.
- Preserve naming and structure conventions:
  - Hooks with `use` prefix.
  - Reusable primitives under `components/base`.
  - Provider composition under `providers`.
- Prioritize mobile/tablet field usage:
  - touch targets at least 44x44,
  - explicit loading/error/empty states,
  - quick-entry forms for unstable connectivity scenarios.
- Do not enforce critical clinical/governance rules only in UI; require backend validation parity.
- Keep changes small and focused; avoid adding new visual primitives when existing design-system primitives can solve the task.
