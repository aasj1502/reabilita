#!/bin/sh
set -e

echo "[backend] Inicializando Reabilita Backend..."

if [ "${DJANGO_USE_SQLITE:-false}" != "true" ]; then
  echo "[backend] Aguardando PostgreSQL em ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
  ATTEMPTS=0
  MAX_ATTEMPTS="${DB_WAIT_MAX_ATTEMPTS:-30}"
  WAIT_SECONDS="${DB_WAIT_INTERVAL_SECONDS:-2}"

  until python - <<'PY'
import os
import sys
import psycopg

host = os.getenv("POSTGRES_HOST", "db")
port = os.getenv("POSTGRES_PORT", "5432")
dbname = os.getenv("POSTGRES_DB", "reabilita")
user = os.getenv("POSTGRES_USER", "reabilita")
password = os.getenv("POSTGRES_PASSWORD", "reabilita")

try:
    connection = psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )
    connection.close()
except Exception:
    sys.exit(1)

sys.exit(0)
PY
  do
    ATTEMPTS=$((ATTEMPTS + 1))
    if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
      echo "[backend] PostgreSQL indisponível após ${ATTEMPTS} tentativas."
      exit 1
    fi

    echo "[backend] Tentativa ${ATTEMPTS}/${MAX_ATTEMPTS} falhou. Nova tentativa em ${WAIT_SECONDS}s..."
    sleep "$WAIT_SECONDS"
  done
fi

echo "[backend] Executando migrações..."
python manage.py migrate --noinput

if [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "[backend] Verificando superusuário padrão..."
  python manage.py seed_admin
fi

if [ "${RUN_SEED_REFERENCIAS:-false}" = "true" ]; then
  echo "[backend] Executando carga de referências clínicas..."
  python manage.py seed_referencias_saude
fi

echo "[backend] Serviço pronto."
exec "$@"
