# Reabilita Backend (bootstrap inicial)

Estrutura inicial criada para Django + DRF com separação por domínio:

- `apps/pessoal`: cadastro de militares e profissionais de saúde.
- `apps/saude`: atendimento clínico com regras de domínio obrigatórias.
- `apps/estatistica`: endpoints iniciais para métricas e dashboards.
- `reabilita_backend/settings`: configuração base e desenvolvimento.

## Regras já estruturadas no modelo de atendimento

- Trava Médica: bloqueia salvamento sem `medico_id`.
- Gatilho S-RED: ativa `flag_sred` para lesão Óssea + Por Estresse ou CID-10 `M84.3`.
- Lateralidade: aplica regra para membros vs. linha média.
- Consistência oncológica: valida CID-O ósseo contra CID-10 `C40-C41`.

## Próximos passos sugeridos

1. Criar ambiente Python e instalar dependências:
   - `pip install -r requirements.txt`
2. Ajustar variáveis de ambiente com base em `.env.example`.
3. (Opcional bootstrap local) usar SQLite com:
   - `DJANGO_USE_SQLITE=true`
4. Criar migrações:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
5. Carregar referências clínicas (CID-10, CID-O, SAC):
   - carga completa inicial: `python manage.py seed_referencias_saude --reset`
   - carga incremental (somente se houver alteração): `python manage.py seed_referencias_saude`
   - carga forçada: `python manage.py seed_referencias_saude --force`
6. Criar superusuário e validar endpoints DRF.

## ETL incremental/versionado

- Detecção de alteração por arquivo via checksum SHA-256.
- Versionamento por fonte em `ReferenciaArquivoVersao`.
- Histórico de execuções em `CargaReferenciaHistorico` com status:
  - `SUCESSO`
  - `SEM_ALTERACAO`
  - `FALHA`

## Endpoints administrativos de carga

- Disparar carga:
  - `POST /api/v1/saude/carga-referencias/`
  - Payload: `{ "reset": true | false, "force": true | false }`
- Consultar histórico:
  - `GET /api/v1/saude/carga-referencias/historico/?limit=20`
- Permissão: usuário autenticado com `is_staff=true`

## Observação

A base ETL incremental/versionada está ativa; próximos incrementos podem incluir versionamento semântico por release e ETL diferencial por lote.
