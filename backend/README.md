# Backend (FastAPI)

## 1) Install dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> Note: `face_recognition` requires system packages (dlib build deps). On Windows/macOS you may need extra steps.

## 2) Set environment variables

Required:
- `GEMINI_API_KEY` (Google Gemini API key)

Optional:
- `FRONTEND_ORIGINS` (comma-separated, default `*`)
- `LOG_LEVEL` (default `INFO`)

Example (Linux/macOS):
```bash
export GEMINI_API_KEY="..."
export FRONTEND_ORIGINS="http://localhost:5173"
```

## 3) Run the server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 4) Test

- Health: `GET http://localhost:8000/health`
- WebSocket: `ws://localhost:8000/ws/scene?language=hi`
