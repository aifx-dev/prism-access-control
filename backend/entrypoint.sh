#!/bin/sh
set -e

# Volumen Docker en /app/media suele ser root:root; la app corre como appuser y no podría escribir fotos.
if [ "$(id -u)" = 0 ]; then
  mkdir -p /app/media
  chown -R appuser:appgroup /app/media
  exec gosu appuser "$0" "$@"
fi

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
