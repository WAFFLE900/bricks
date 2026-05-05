# BRICKS 專案總覽

## 專案簡介

BRICKS 是一個協作型專案與會議紀錄平台，採前後端分離架構，主要由三個模組組成：

- 資料庫：PostgreSQL（搭配 Alembic migration）
- 後端：FastAPI（Python + SQLAlchemy）
- 前端：Vue 3 + Vite + Pinia

## 功能簡介

- 使用者註冊、登入、JWT 驗證
- Google / Facebook OAuth 登入與社群帳號綁定
- 專案管理（建立、分類、結束、垃圾桶）
- 專案成員邀請與權限管理（owner / edit / view）
- 會議紀錄（Record / Text Box）與標籤系統
- 專案搜尋、提及通知與通知已讀管理

## 怎麼啟動

### 方式一：一鍵啟動整個專案（推薦）

```powershell
cd C:\bricks
Copy-Item .env.example .env
docker compose up --build
```

啟動後預設入口：

- 前端：`http://localhost:8080`
- 後端 API：`http://localhost:8000/api/v1`
- 後端 Swagger：`http://localhost:8000/docs`

### 方式二：分模組啟動

- 資料庫文件：`C:\bricks\infra\README.md`
- 後端文件：`C:\bricks\apps\api\README.md`
- 前端文件：`C:\bricks\apps\web\README.md`

