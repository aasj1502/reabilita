# Deploy Docker + Portainer (Reabilita)

Este guia prepara o projeto para execução em ambiente de teste com Docker e Portainer.

## 1) Arquivos adicionados

- `docker-compose.yml`: execução local (com build local das imagens).
- `docker-compose.stack.yml`: deploy em Stack Portainer (Swarm) com imagens pré-buildadas.
- `.env.example`: variáveis necessárias para ambos cenários.
- `reabilita-backend/Dockerfile`
- `reabilita-backend/docker/entrypoint.sh`
- `reabilita-backend/.dockerignore`
- `reabilita-frontend/Dockerfile`
- `reabilita-frontend/nginx/default.conf`
- `reabilita-frontend/.dockerignore`

## 2) Pré-requisitos

- Docker 24+
- Docker Compose plugin
- (Para Stack Portainer) ambiente Swarm ativo e Portainer com acesso ao cluster

## 3) Configurar variáveis

No diretório raiz do projeto:

1. Copie o arquivo de exemplo:
   - Linux/macOS: `cp .env.example .env`
   - PowerShell: `Copy-Item .env.example .env`
2. Ajuste valores mínimos:
   - `DJANGO_SECRET_KEY` (veja seção abaixo)
   - `POSTGRES_PASSWORD`
   - `DJANGO_ALLOWED_HOSTS` (domínio/IP do ambiente de teste)

### Como gerar a DJANGO_SECRET_KEY

A `DJANGO_SECRET_KEY` deve ser uma string longa, aleatória e secreta. Use um dos métodos abaixo para gerar:

**Python (recomendado):**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Python (sem Django instalado):**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**PowerShell:**

```powershell
-join ((65..90)+(97..122)+(48..57)+(33,35,36,37,38,42,43,45) | Get-Random -Count 50 | ForEach-Object {[char]$_})
```

Copie a saída e cole como valor de `DJANGO_SECRET_KEY` no `.env` (local) ou nas **Environment variables** da Stack no Portainer. Nunca reutilize a mesma chave entre ambientes.

## 4) Subir localmente com Docker Compose

No diretório raiz:

```bash
docker compose --env-file .env up -d --build
```

Serviços:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

Parar ambiente:

```bash
docker compose down
```

Parar e remover volume do banco:

```bash
docker compose down -v
```

## 5) Deploy via Portainer Stack (Swarm)

### 5.1 Build e push das imagens

Execute no diretório raiz:

```bash
docker build -t aasj1502/reabilita-backend:latest ./reabilita-backend
docker build -t aasj1502/reabilita-frontend:latest ./reabilita-frontend

docker push aasj1502/reabilita-backend:latest
docker push aasj1502/reabilita-frontend:latest
```

### 5.2 Criar Stack no Portainer

1. Em **Stacks > Add stack**.
2. Dê um nome, por exemplo: `reabilita`.
3. Cole o conteúdo de `docker-compose.stack.yml`.
4. Em **Environment variables**, adicione as variáveis de `.env.example` (adaptadas para o ambiente).
5. Deploy da stack.

### 5.3 Bloco pronto de variáveis (copiar e colar)

Use este bloco como base em **Environment variables** da Stack no Portainer:

```env
FRONTEND_PORT=5173
BACKEND_PORT=8000
POSTGRES_PORT=5432

DJANGO_SETTINGS_MODULE=reabilita_backend.settings.dev
DJANGO_SECRET_KEY=troque-esta-chave
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,SEU_DOMINIO_OU_IP
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin
DJANGO_SUPERUSER_EMAIL=admin@saude.com
RUN_SEED_REFERENCIAS=false
DB_WAIT_MAX_ATTEMPTS=30
DB_WAIT_INTERVAL_SECONDS=2

POSTGRES_DB=reabilita
POSTGRES_USER=reabilita
POSTGRES_PASSWORD=troque-esta-senha

BACKEND_IMAGE=aasj1502/reabilita-backend:latest
FRONTEND_IMAGE=aasj1502/reabilita-frontend:latest
```

Observações do bloco:

- Se usar domínio público, inclua o domínio em `DJANGO_ALLOWED_HOSTS`.
- Para primeira carga clínica automática, altere `RUN_SEED_REFERENCIAS=true`.
- Se mapear portas diferentes no host, ajuste `FRONTEND_PORT` e `BACKEND_PORT`.

## 6) Comportamento de inicialização

O backend usa `entrypoint.sh` para:

1. aguardar o PostgreSQL ficar disponível,
2. executar `python manage.py migrate --noinput`,
3. iniciar a aplicação.

Se `RUN_SEED_REFERENCIAS=true`, o backend executa também:

```bash
python manage.py seed_referencias_saude
```

## 7) Saúde dos serviços

Teste rápido dos endpoints:

- Backend root: `GET /`
- Auth CSRF: `GET /api/v1/auth/csrf/`
- Frontend: abrir `/dashboard` após login

## 8) Observações importantes

- Este setup está orientado a **ambiente de teste**.
- O frontend roda em Nginx e faz proxy para backend em `/api`, `/admin` e `/static`.
- Para produção, recomenda-se endurecimento adicional (TLS, secret manager, WSGI robusto, observabilidade e backup do volume PostgreSQL).
