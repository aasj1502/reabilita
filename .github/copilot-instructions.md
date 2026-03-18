# Project Guidelines — Sistema Reabilita

## Escopo e estado atual
- Este workspace usa apenas `.github/copilot-instructions.md`; não criar `AGENTS.md` em paralelo.
- Estado real do repositório:
	- `reabilita-backend/` possui bootstrap Django/DRF inicial (`manage.py`, `requirements.txt`, `reabilita_backend/`, `apps/`) e documentação/dados em `dados/`.
	- `reabilita-frontend/` possui bootstrap React + Vite + TypeScript e design system em `src/design-system/`.
- Projeto ainda em implantação; parte das regras e integrações avançadas segue em evolução incremental.

## Stack e arquitetura alvo
- Backend alvo: Python 3.x + Django + Django REST Framework + PostgreSQL.
- Frontend alvo: React + TypeScript (TSX) + Axios + TanStack Query.
- Fluxo esperado: serializers DRF → contrato de API → types/interfaces TS → consumo por services/hooks React.

## Contratos e segurança (instruções estritas)
- Toda interface/type no React deve refletir exatamente o schema de saída dos serializers do Django.
- Sempre validar permissões no backend (Django Permissions) antes de separar fluxos entre Médico, Instrutor e demais perfis.
- Não implementar regras críticas apenas na UI quando houver impacto clínico, de segurança ou de governança de dados.

## Regras de domínio obrigatórias
- Trava Médica: impedir salvamento de atendimento sem `medico_id` válido.
- Gatilho S-RED: lesão Óssea + origem Por Estresse (ou CID-10 `M84.3`) deve ativar `flag_sred` e protocolo multidisciplinar.
- Lateralidade: Direita/Esquerda/Bilateral para membros; “Não é o caso” para estruturas de linha média (ex.: coluna/core).
- Consistência oncológica: morfologias CID-O ósseas (ex.: `M9180/3`) devem ser compatíveis com CID-10 `C40-C41`.

## Convenções de frontend (uso em campo)
- O design system em `reabilita-frontend/src/design-system/` é a fonte de verdade de UI.
- Seguir padrões já existentes:
	- componentes base em `components/base`;
	- hooks com prefixo `use`;
	- providers compostos em `providers`.
- Priorizar usabilidade mobile/tablet: áreas de toque mínimas de 44x44, entradas rápidas e estados explícitos de loading/erro para conexões oscilantes.
- Manter estilo consistente com o código existente (tipagem explícita, imports tipados, mudanças pequenas e focadas).

## Build, teste e execução
- Backend (escopo inicial):
	- instalar dependências: `pip install -r reabilita-backend/requirements.txt`
	- migrações: `python manage.py makemigrations && python manage.py migrate` (dentro de `reabilita-backend/`)
- Frontend (escopo inicial):
	- instalar dependências: `npm install` (dentro de `reabilita-frontend/`)
	- desenvolvimento: `npm run dev`
- Se houver falhas de ambiente, declarar lacunas explicitamente e propor correção mínima antes de avançar.
- Para reutilização isolada do design system, consultar dependências mínimas em `reabilita-frontend/src/design-system/README.md`.

## Fontes de verdade
- `reabilita-frontend/fontes/plan_des_reabilita.md`
- `reabilita-backend/dados/modelagem_banco_dados.md`
- `reabilita-backend/dados/mapeamento_dados_orto.md`
- `reabilita-backend/dados/modelagem_dados.md`
- `reabilita-frontend/src/design-system/README.md`

## Boas práticas do agente neste workspace
- Preferir alterações pequenas e cirúrgicas, respeitando o estado atual (projeto ainda em implantação).
- Não inventar arquivos/comandos inexistentes; declarar lacunas com clareza.
- Ao criar novas estruturas, manter modularização por domínio:
	- backend: apps, models, serializers, views, permissions;
	- frontend: components, hooks, services, types.
- Documentar decisões e fluxos de dados em Markdown para manter rastreabilidade de negócio.