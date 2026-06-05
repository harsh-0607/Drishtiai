# DRISHTI AI

Browser-based AI assistant for visually impaired users in India.

## Quick start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY="..."  # required
export MONGODB_URI="mongodb://localhost:27017"  # optional (default local)
export REDIS_URL="redis://localhost:6379/0"  # optional

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

## Services

- Health: `GET /health`
- WebSocket scene: `WS /ws/scene?language=hi`
- REST scene: `POST /api/scene/describe`
- REST ocr: `POST /api/ocr/read`
- REST face: `POST /api/face/register`, `POST /api/face/recognize`

