---
description: "Use when updating domain Markdown documentation without breaking clinical, data, or governance consistency in Reabilita."
name: "Atualizar documentação clínica consistente"
argument-hint: "Ex.: Atualizar regra de lateralidade no mapeamento SAC"
agent: "agent"
---

Atualize a documentação de domínio do Reabilita com base no pedido do usuário (argumento do prompt), mantendo consistência clínica e rastreabilidade técnica.

Escopo prioritário de arquivos:
- `reabilita-frontend/fontes/**/*.md`
- `reabilita-backend/dados/**/*.md`

Regras obrigatórias que não podem ser quebradas:
- Trava Médica: sem `medico_id` válido, atendimento não deve ser salvo.
- Gatilho S-RED: lesão Óssea + origem Por Estresse (ou CID-10 `M84.3`) ativa `flag_sred` e protocolo multidisciplinar.
- Lateralidade: Direita/Esquerda/Bilateral para membros; “Não é o caso” para estruturas de linha média.
- Consistência oncológica: CID-O ósseo (ex.: `M9180/3`) compatível com CID-10 `C40-C41`.

Fluxo de trabalho:
1. Identifique quais documentos são impactados pelo pedido.
2. Aplique alterações pequenas e focadas, sem reescrever seções não relacionadas.
3. Mantenha separação explícita entre estado atual, arquitetura alvo e proposta futura.
4. Reconcile termos/campos entre documentos (ex.: `tipo_lesao`, `lateralidade`, `codigo_cid10`, `codigo_cido`, `flag_sred`).
5. Se houver conflito entre documentos, normalize com base nas fontes de verdade e explicite a decisão.

Fontes de verdade para validação cruzada:
- `reabilita-frontend/fontes/plan_des_reabilita.md`
- `reabilita-backend/dados/modelagem_banco_dados.md`
- `reabilita-backend/dados/mapeamento_dados_orto.md`
- `reabilita-backend/dados/modelagem_dados.md`

Formato de saída esperado:
- Resumo curto do que foi alterado.
- Lista de arquivos alterados.
- Checklist de consistência (Trava Médica, S-RED, Lateralidade, Oncológica) com status.
- Pendências/assunções, se existirem.
