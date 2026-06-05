# DRISHTI AI

Browser-based AI assistant for visually impaired users in India.

## Quick start (Docker)

```bash
export GEMINI_API_KEY="..."  # required for scene descriptions

docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`

## Quick start (Local dev)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

export GEMINI_API_KEY="..."
export MONGODB_URI="mongodb://localhost:27017"
export REDIS_URL="redis://localhost:6379/0"
export FIREBASE_PROJECT_ID="..."              # optional if auth enabled
export FIREBASE_SERVICE_ACCOUNT_JSON="..."    # optional (path or raw json)

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## APIs

### REST
- `POST /api/scene/describe`
- `POST /api/ocr/read`
- `POST /api/face/register`
- `POST /api/face/recognize`
- `POST /api/speech/transcribe`
- `POST /api/speech/tts`
- `POST /api/navigate/obstacles`

### WebSocket
- `WS /ws/scene?language=hi` (scene only)
- `WS /ws/stream?language=hi&user_id=...` (unified stream: scene/obstacles/face)

