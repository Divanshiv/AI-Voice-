# AI Voice Assistant (Free Prototype)

An interactive AI voice chat assistant where users speak commands and AI responds with voice. Built using **100% FREE** tools and APIs.

## Features

- 🎤 Voice Input (FREE) - Web Speech API built into Chrome/Edge
- 🔊 Voice Output (FREE) - Web Speech Synthesis built into all browsers  
- 🤖 AI Engine - Google Gemini (Free Tier)
- 📱 Modern UI - Next.js 14 + Tailwind CSS + Framer Motion
- 💾 Conversation Memory - In-memory (MongoDB optional)

## Tech Stack

### Frontend
- Next.js 14 (App Router)
- React
- Tailwind CSS
- Framer Motion
- Web Speech API (FREE - browser built-in)
- Web Speech Synthesis API (FREE - browser built-in)

### Backend
- FastAPI (Python)
- Google Gemini API (Free Tier: 60 requests/min, 1500/day)
- MongoDB Atlas (FREE tier - optional)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- Chrome or Edge browser (for voice features)

### Quick Start

1. **Clone and setup**

```bash
# Frontend
cd frontend
npm install

# Backend  
cd ../backend
pip install -r requirements.txt
```

2. **Configure API Keys**

Get free Gemini API key: https://makersuite.google.com/app/apikey

```bash
# backend/.env
GEMINI_API_KEY=your-gemini-api-key-here
```

3. **Run the application**

Terminal 1 - Backend:
```bash
cd backend
python main.py
# Runs on http://localhost:8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
# Opens http://localhost:3000
```

4. **Use the app**

1. Open http://localhost:3000 in Chrome or Edge
2. Click "Start Conversation"
3. Allow microphone access when prompted
4. Speak your message
5. AI responds with voice

## Project Structure

```
ai-voice/
├── frontend/                 # Next.js 14 app
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx     # Landing page
│   │   │   ├── chat/       # Chat page
│   │   │   └── layout.tsx  # Root layout
│   │   ├── lib/
│   │   │   ├── api.ts      # API client
│   │   │   └── voice.ts    # Voice utilities
│   │   └── globals.css    # Tailwind + custom styles
│   └── package.json
│
├── backend/                # FastAPI app
│   ├── main.py             # Entry point
│   ├── app/
│   │   ├── config.py       # Settings
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # AI, conversation
│   │   ├── models/        # Pydantic models
│   │   └── database/     # MongoDB connection
│   ├── product_info.json   # Product data
│   └── requirements.txt
│
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message, get AI response |
| `/api/chat/history/{session_id}` | GET | Get conversation history |
| `/api/health` | GET | Health check |

## Usage Examples

Voice Commands:
- "Hello" / "Hi" - Start conversation
- "Tell me about your product" - Get product info
- "Repeat" - Hear last response again
- "Goodbye" / "Exit" - End conversation

## Browser Support

- **Chrome** - Full voice support ✓
- **Edge** - Full voice support ✓
- **Safari** - Limited support (no SpeechRecognition)

## Troubleshooting

1. **Microphone not working**: Ensure Chrome/Edge and grant mic permission
2. **API errors**: Check GEMINI_API_KEY in .env
3. **CORS errors**: Check FRONTEND_URL matches your frontend

## License

MIT