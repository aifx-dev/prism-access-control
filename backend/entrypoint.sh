#!/bin/sh
set -e

echo "Esperando a que PostgreSQL esté listo..."
# El contenedor ya depende de db (condition: healthy), pero dejamos una pequeña pausa de seguridad
sleep 2

if [ "${RUN_MIGRATIONS:-0}" = "1" ] || [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "Ejecutando migraciones con Alembic..."
  alembic upgrade head
else
  echo "Migraciones desactivadas (RUN_MIGRATIONS=$RUN_MIGRATIONS)."
fi

echo "Iniciando servidor Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
