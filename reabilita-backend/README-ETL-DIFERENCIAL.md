# ETL Diferencial por Linha — Auditoria e Versioning

## Visão Geral

O sistema implementou auditoria granular por registro com detecção de mudanças via hash SHA-256. Cada linha de CSV é processada de forma inteligente:

- **CRIADO**: Novo registro (primeira carga)
- **ATUALIZADO**: Registro existente com mudanças detectadas
- **INALTERADO**: Registro sem mudanças (hash idêntico)

## Modelos de Banco de Dados

### `RecordChangeAudit`
Tabela de auditoria que registra mudanças por linha:
- `tabela`: Nome da tabela (Cid10Categoria, CidOMorfologia, SacMapeamento)
- `registro_id`: ID do registro modificado
- `chave_registra`: Chave única (ex: código CID-10)
- `tipo_mudanca`: CRIADO, ATUALIZADO ou INALTERADO
- `hash_anterior`: SHA-256 anterior (vazio se CRIADO)
- `hash_novo`: SHA-256 novo após mudança
- `dados_alterados`: JSON com campos alterados {campo: [anterior, novo]}
- `historico_carga`: FK para CargaReferenciaHistorico (auditoria associada)

### Campos de Hash
Adicionados aos modelos de referência:
- `Cid10Categoria.record_hash`: SHA-256 do registro
- `CidOMorfologia.record_hash`: SHA-256 do registro
- `SacMapeamento.record_hash`: SHA-256 do registro

## Fluxo de Carga

### 1. Leitura e Normalização
```python
# CSV → Dicionários com chaves normalizadas
# Encoding fallback: utf-8-sig → cp1252 → latin-1
```

### 2. Computação de Hash
```python
def _compute_record_hash(data: dict[str, str]) -> str:
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()
```

Garante hash consistente independente da ordem das chaves.

### 3. Comparação e Upsert Inteligente
Para cada registro:
1. **Hash não existe** (new record):
   - Cria novo registro com hash
   - Registra auditoria: CRIADO
2. **Hash diferente** (record changed):
   - Detecta mudanças campo por campo
   - Atualiza registro e hash
   - Registra auditoria: ATUALIZADO (com diff)
3. **Hash idêntico** (no change):
   - Pula processamento
   - Registra auditoria: INALTERADO (para rastreamento)

### 4. Histórico e Rastreabilidade
Cada carga registra:
- Status (SUCESSO, SEM_ALTERACAO, FALHA)
- Resumo por tabela (criados, atualizados, inalterados)
- Link bidirecional com RecordChangeAudit

## Testes Validados

### Cenário 1: Carga Inicial (--reset)
```bash
$ python manage.py seed_referencias_saude --reset

Resultado:
- CID-10: 2045 CRIADO
- CID-O: 816 CRIADO
- SAC: 6 CRIADO + 10 ATUALIZADO (normalização de chaves)
```

### Cenário 2: Sem Mudanças (re-execução normal)
```bash
$ python manage.py seed_referencias_saude

Resultado: SEM_ALTERACAO
- Nenhum arquivo processado (checksum idêntico)
```

### Cenário 3: Força de Reprocessamento (--force)
```bash
$ python manage.py seed_referencias_saude --force

Resultado: SUCESSO
- Todos arquivos reprocessados
- CID-10: 2045 INALTERADO
- CID-O: 816 INALTERADO
- SAC: 5 INALTERADO + 11 ATUALIZADO (normalização)
```

### Cenário 4: Mudança Detectada
```bash
$ # Modificar um CSV
$ python manage.py seed_referencias_saude

Resultado: SUCESSO
- Arquivo alterado detectado via checksum
- Registros modificados marcados como ATUALIZADO
- Auditoria registra campo e valores anterior/novo
```

## Benefícios

1. **Rastreamento Completo**: Cada mudança registrada com timestamp e histórico
2. **Auditoria Granular**: Saber exatamente qual campo mudou em qual registro
3. **Eficiência**: Pula registros inalterados, economiza I/O
4. **Incremental**: Suporta cargas incrementais sem reset
5. **Derivação**: Fácil implementar sincronização com sistemas externos

## Endpoints de Admin

### GET `/api/v1/saude/carga-referencias/historico/?limit=20`
Retorna histórico paginado de cargas com resumo.

### POST `/api/v1/saude/carga-referencias/`
Aceita query params:
- `reset=true`: Limpa tabelas antes de carregar
- `force=true`: Força reprocessamento mesmo sem mudanças

Retorna resumo da carga e historico_id.

## Django Admin

Via `/admin/saude/recordchangeaudit/`:
- Filtrar por tabela, tipo de mudança, data
- Visualizar hashes e campos alterados
- Link direto para histórico de carga

## Próximas Melhorias

- [ ] Frontend admin console para visualizar mudanças
- [ ] Excel export de auditoria
- [ ] Webhooks para integração com sistemas externos
- [ ] Reverse-sync (detectar mudanças em BD e sincronizar para CSV)
- [ ] Compressão de histórico (manter últimas N cargas)
