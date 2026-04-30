# VPS: Edge Guard con Docker (Postgres ya en la máquina)

**Asumido:** Docker, PostgreSQL + pgvector en el host, en una carpeta (ej. `/opt/prism/`) tienes **`docker-compose.yml`**, **`.env.backend`**, **`.env.admin`**, y **`docker login`** si las imágenes son privadas.

Imágenes por defecto: `aifxnetworks/edge-guard-backend:latest`, `aifxnetworks/edge-guard-admin:latest`.

**No uses `--env-file`:** en muchas VPS el comando es `docker compose` sin ese flag (o ni siquiera existe el flag). Las variables de la API van en **`.env.backend`** y las del admin en **`.env.admin`** (`env_file` en el compose). Puertos e imágenes usan **valores por defecto en el YAML** salvo que crees un **`.env`** al lado del compose solo con claves de interpolación (`BACKEND_PORT`, `BACKEND_IMAGE`, etc.) — Compose carga automáticamente ese `.env` si existe.

Si no tienes el plugin V2, usa **`docker-compose`** (guión) en los mismos comandos.

---

## 1. Archivos en la VPS

Misma carpeta:

- `docker-compose.yml`
- `.env.backend`
- `.env.admin`

---

## 2. `POSTGRES_URL` en `.env.backend`

Desde el contenedor, **`localhost` no es el host**. Ejemplo (ajusta usuario, clave, host, base):

```env
POSTGRES_URL=postgresql+asyncpg://USUARIO:CLAVE@172.17.0.1:5432/edge_guard
```

En la base (una vez):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 3. Comandos

```bash
cd /opt/prism
```

```bash
docker compose config --quiet
```

(Si falla: `docker-compose config --quiet`.)

```bash
docker compose pull && docker compose up -d
```

Primera vez con BD vacía: en **`.env.backend`** pon `RUN_MIGRATIONS=1`, luego otra vez `docker compose up -d`. Cuando vaya bien, `RUN_MIGRATIONS=0` y:

```bash
docker compose up -d --force-recreate backend
```

```bash
docker compose logs -f backend
```

```bash
curl -sS http://127.0.0.1:8000/health
```

Admin (puerto 5173 por defecto):

```bash
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5173/
```

---

## 4. Parar

```bash
cd /opt/prism
docker compose down
```

---

## 5. Actualizar imágenes

```bash
cd /opt/prism
docker compose pull && docker compose up -d
```

Esquema nuevo en BD: `RUN_MIGRATIONS=1` una vez, `up -d`, revisar logs, volver a `0`.

---

## 6. Plugin Compose (si `docker: 'compose' is not a docker command`)

Debian/Ubuntu:

```bash
sudo apt-get update && sudo apt-get install -y docker-compose-plugin
docker compose version
```

---

## 7. Plantillas desde el repo

```bash
cd deploy/vps
cp .env.backend.example .env.backend
cp .env.admin.example .env.admin
```

Edita y sube los tres ficheros a la VPS; §3.

---

Definición del stack: **`deploy/vps/`**. Secretos: no versionar **`.env.backend`** / **`.env.admin`** (gitignore).
