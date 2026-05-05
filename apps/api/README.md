# BRICKS 後端（API）

## 入口

- 應用入口：`C:\bricks\apps\api\app\main.py`
- API 路由入口：`C:\bricks\apps\api\app\api\router.py`
- 設定入口：`C:\bricks\apps\api\app\core\config.py`

## 功能簡介

- 身份驗證：註冊、登入、JWT、`/auth/me`
- OAuth：Google / Facebook 登入與帳號綁定
- 使用者：個人資料更新、密碼更新、搜尋紀錄
- 專案：建立、查詢、編輯、結束、垃圾桶、刪除
- 專案協作：成員邀請、權限管理（`owner` / `edit` / `view`）
- 紀錄管理：Record / Text Box CRUD、提及通知
- 標籤與搜尋：Tag 綁定、專案搜尋排序
- 通知：通知列表、單筆已讀、全部已讀

## 怎麼啟動

### 本機開發模式

```powershell
cd C:\bricks
docker compose up -d postgres

cd C:\bricks\apps\api
uv sync
$env:DATABASE_URL="postgresql+psycopg://bricks:bricks@localhost:5432/bricks"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

啟動後：

- API Base：`http://localhost:8000/api/v1`
- Swagger：`http://localhost:8000/docs`

### 測試

```powershell
cd C:\bricks\apps\api
uv run pytest
```
