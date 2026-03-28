# Frontend

This frontend is a Vue 3 + Vite application with Cesium-based map views.

## Runtime Requirements

- Node.js `^20.19.0 || >=22.12.0`
- npm `>=10`
- Backend API available on `http://127.0.0.1:8000` by default
- Free local ports:
  - `8000` for backend
  - `4173` for frontend dev server

## Manual Startup

Install dependencies:

```sh
npm ci
```

Run the dev server:

```sh
npm run dev -- --host 127.0.0.1 --port 4173 --strictPort
```

Override the backend API base URL when needed:

```sh
set VITE_API_BASE_URL=http://127.0.0.1:8001
npm run dev -- --host 127.0.0.1 --port 4173 --strictPort
```

## One-Click Full Stack Startup

From the repository root, the browser now opens the frontend page automatically after startup succeeds:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_platform.ps1
```

Or double click / run:

```cmd
scripts\start_platform.cmd
```

Skip browser auto-open:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_platform.ps1 -NoBrowser
```

Stop both services:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop_platform.ps1
```

## Build

```sh
npm run build
```
