# BRICKS 資料庫（Database）

## 入口

- 本地資料庫服務入口：`C:\bricks\docker-compose.yml`（`postgres` service）
- migration 入口：`C:\bricks\apps\api\alembic\env.py`
- migration 版本檔：`C:\bricks\apps\api\alembic\versions`

## 功能簡介

- 提供 BRICKS 主資料庫（PostgreSQL 16）
- 持久化資料 volume：`postgres-data`
- 由 Alembic 管理 schema 版本與升級
- 支援選配 `pgAdmin`（`pgadmin` profile）供本機管理

## 怎麼啟動

### 啟動 PostgreSQL（本機）

```powershell
cd C:\bricks
Copy-Item .env.example .env
docker compose up -d postgres
```

### 套用 migration

```powershell
cd C:\bricks\apps\api
uv sync
$env:DATABASE_URL="postgresql+psycopg://bricks:bricks@localhost:5432/bricks"
uv run alembic upgrade head
```

### （選配）啟動 pgAdmin

```powershell
cd C:\bricks
docker compose --profile pgadmin up -d pgadmin
```

- pgAdmin 預設網址：`http://localhost:5050`
- 帳號密碼來源：`.env` 內的 `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD`
