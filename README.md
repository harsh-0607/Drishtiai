# Drishtiai
🦯 DRISHTI AI — Real-time browser-based AI assistant for visually impaired individuals. No app. No hardware. Just a browser tab and independence.


# 👁️ DRISHTI AI
### AI-Powered Eyes for the Visually Impaired

> *"12 million blind Indians. One browser tab. Zero excuses."*

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini_Vision-Google-4285F4?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Hackathon](https://img.shields.io/badge/WEBNOVA_2026-National_Hackathon-gold?style=for-the-badge)

---

## 🌟 What is DRISHTI?

**DRISHTI** (दृष्टि — meaning *Vision* in Hindi) is a browser-native,
AI-powered visual assistant built specifically for the 12+ million
visually impaired individuals across India.

Unlike expensive hardware devices or English-only apps, DRISHTI runs
entirely inside a mobile browser — no installation, no costly device,
no permanent internet connection required. It uses the phone's camera
as a pair of intelligent eyes, powered by Python AI on the backend,
to describe the world in real-time in the user's own language.

---

## 😔 The Problem

India has the **largest visually impaired population in the world** —
over 12 million people — yet:

- ❌ Smart canes cost **₹40,000–₹80,000** — unaffordable for most
- ❌ Existing AI apps are **English-only** — useless for rural India
- ❌ Most solutions require **app downloads** on high-end phones
- ❌ Cloud-based tools fail in **low/no connectivity** rural zones
- ❌ **68% of blind individuals** in India live below the poverty line

The result is dependency, isolation, and loss of dignity —
all preventable with the right technology.

---

## ✅ Our Solution

DRISHTI bridges this gap with one radical insight:

> Every visually impaired person in India already owns the world's
> most powerful assistive device — a smartphone with a camera and
> a browser. The missing piece is the AI layer.

DRISHTI provides:

- 🎯 **Real-time scene description** — AI narrates surroundings
  continuously via camera
- 📖 **Multilingual OCR** — reads medicine labels, currency notes,
  menus, and signs aloud
- 👤 **Face recognition** — identifies registered family members
  and friends by name
- 🧭 **Navigation assistance** — detects obstacles, steps, and
  doors with directional audio cues
- 🎙️ **Voice commands** — fully hands-free interaction in any
  Indian language
- 🌐 **22+ Indian languages** — Hindi, Tamil, Telugu, Bengali,
  Marathi, and more
- 📴 **Offline mode** — core features work without internet
  after first load

---

## ⚙️ Tech Stack

### Backend (Python — Core Intelligence)
| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Scene AI | Google Gemini Vision API |
| Object Detection | YOLOv8 (Ultralytics) |
| OCR | EasyOCR + Pytesseract |
| Face Recognition | face_recognition + DeepFace |
| Speech-to-Text | faster-whisper (OpenAI Whisper) |
| Text-to-Speech | gTTS + edge-tts |
| Real-time Stream | WebSockets |
| Database | MongoDB (Motor async) |
| Cache | Redis |
| Auth | Firebase Admin SDK |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React.js + TypeScript |
| Styling | Tailwind CSS |
| Camera Access | WebRTC + MediaDevices API |
| Voice I/O | Web Speech API + SpeechSynthesis |
| PWA / Offline | Service Worker + Workbox |
| Real-time | Socket.io Client |

---

## 🏗️ System Architecture
User's Phone Browser
│
│  Camera frames + Voice
▼
React.js PWA
(WebRTC + Web Speech API)
│
│  WebSocket / REST API
▼
FastAPI Server (Python)
│
┌────┴─────────────────────┐
│                          │
▼                          ▼
AI/ML Engine              Database

Gemini Vision           - MongoDB
YOLOv8                  - Redis Cache
EasyOCR                 - Firebase Auth
face_recognition
faster-whisper
gTTS / edge-tts
│
│  Audio response
▼
User hears description
in their own language


---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB running locally or Atlas URI
- Google Gemini API key

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/drishti-ai.git
cd drishti-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (system dependency)
sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-tam

# Set environment variables
cp .env.example .env
# Add your GEMINI_API_KEY, MONGODB_URI, FIREBASE credentials

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker (Recommended)
```bash
# Run everything with one command
docker-compose up --build
```

---

## 📁 Project Structure
drishti-ai/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── routers/
│   │   ├── scene.py             # Scene description
│   │   ├── ocr.py               # Text recognition
│   │   ├── face.py              # Face recognition
│   │   ├── speech.py            # STT + TTS
│   │   └── navigate.py          # Obstacle detection
│   ├── services/
│   │   ├── gemini_service.py    # Google Gemini Vision
│   │   ├── yolo_service.py      # YOLOv8 detection
│   │   ├── ocr_service.py       # EasyOCR + Tesseract
│   │   ├── face_service.py      # Face recognition
│   │   ├── whisper_service.py   # Speech-to-text
│   │   └── tts_service.py       # Text-to-speech
│   ├── database/
│   │   ├── mongodb.py
│   │   └── redis_cache.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Camera.tsx
│   │   │   ├── VoiceInput.tsx
│   │   │   ├── AudioOutput.tsx
│   │   │   └── FaceRegister.tsx
│   │   └── App.tsx
│   ├── public/
│   │   └── manifest.json
│   └── vite.config.ts
│
├── docker-compose.yml
├── .env.example
├── LICENSE
└── README.md

---

## 🎯 Key Features In Detail

### 🔍 Real-Time Scene Description
Camera streams at 2fps to Gemini Vision API.
AI generates natural language descriptions like:
*"Aapke saamne ek darwaza hai. Baaye haath mein
ek vyakti khada hai. Seedhi neeche hai."*

### 📝 OCR Text Reading
EasyOCR supports Devanagari, Tamil, Telugu and 20+
Indian scripts. Points camera at any text — medicine
bottle, bus number, shop sign — and hears it read aloud.

### 👥 Face Recognition
Register family members once. face_recognition library
creates 128-dimensional facial embeddings stored in MongoDB.
Live frames compared in real-time — user hears:
*"Yeh aapki maa Sunita hain, 3 foot door."*

### 🗣️ 22+ Indian Language Support
faster-whisper auto-detects spoken language.
gTTS + edge-tts respond in the same language.
No language selection needed — just speak naturally.

### 📴 Offline-First PWA
Service Worker caches the app shell and lightweight
on-device models (YOLOv8-nano, Tesseract) after
first load. Core features work on 2G or no connection.

---

## 📊 Impact

| Metric | Value |
|---|---|
| Target users in India | 12 million+ |
| Cost to end user | ₹0 (free) |
| Languages supported | 22+ Indian languages |
| Minimum phone required | Any ₹4,000 Android |
| Internet required | No (offline mode) |
| App download required | No (browser-native) |

---

## 🏆 Built For

> **WEBNOVA 2026** — National Level Web Development Hackathon
> IMS Engineering College (IMSEC), Ghaziabad
> In collaboration with HackerRank Campus Crew
> Theme: Healthcare + AI-Powered Web + Social Impact

---

## 🤝 Contributing

Pull requests are welcome. For major changes,
please open an issue first to discuss what you
would like to change.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- Google Gemini Vision API
- OpenAI Whisper
- Ultralytics YOLOv8
- EasyOCR by JaidedAI
- face_recognition by ageitgey
- National Association for the Blind, India

---

<p align="center">
  Built with ❤️ for 12 million Indians who deserve
  to see the world on their own terms.
</p>

<p align="center">
  <b>DRISHTI — Because independence is not a luxury.</b>
</p>
