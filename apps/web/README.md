# BRICKS 前端（Web）

## 入口

- 前端啟動入口：`C:\bricks\apps\web\src\app\main.ts`
- 路由入口：`C:\bricks\apps\web\src\app\router\index.ts`
- API 環境設定入口：`C:\bricks\apps\web\src\shared\config\env.ts`

## 功能簡介

- 登入與註冊流程（含 OAuth callback）
- 問卷與個人資料頁
- 專案總覽與專案列表（含狀態分類）
- 會議紀錄工作區（Record / Text Box）
- 通知、標籤與 API 串接
- 以 Pinia 管理使用者狀態，Vue Router 控制權限導向

## 怎麼啟動

### 本機開發模式

```powershell
cd C:\bricks\apps\web
npm install
$env:VITE_API_BASE_URL="http://localhost:8000/api/v1"
npm run dev -- --host 0.0.0.0 --port 5173
```

啟動後：

- 前端（Vite Dev Server）：`http://localhost:5173`

### 建置與預覽

```powershell
cd C:\bricks\apps\web
npm run build
npm run preview -- --host 0.0.0.0 --port 4173
```
