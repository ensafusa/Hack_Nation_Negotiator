# Hack_Nation_Negotiator 🤖💰

An AI-powered negotiation engine that searches for home improvement ("aménagement") providers, calls them via AI voice agents, negotiates pricing, and returns the best deal to the user.

## How It Works

```
1. 🔍 Search    → Tavily finds providers (phone numbers extracted from results)
2. 📞 Call      → ElevenLabs AI agent calls each provider
3. 🗣️ Negotiate → AI negotiates the best price
4. 💾 Store     → Final price extracted from transcript & saved in memory
5. 🏆 Compare   → Best price returned to the user
```

## Architecture

```
Hack_Nation_Negotiator/
├── backend/          # FastAPI (Python 3.10+)
│   └── app/
│       ├── api/      # Route handlers (thin, no logic)
│       ├── services/ # Business logic (search, voice, extraction, memory)
│       ├── clients/  # Vendor SDK wrappers (Tavily, ElevenLabs, OpenAI, Twilio)
│       └── models/   # Pydantic schemas
└── frontend/         # React 19 + Tailwind CSS
    ├── src/
    │   ├── components/  # SearchForm, NegotiationMonitor, BestPrice
    │   └── context/     # Global state (Context API)
    └── public/
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.10+) |
| Provider Discovery | Tavily Search API |
| Voice Negotiation | ElevenLabs Conversational AI + Twilio |
| Intelligence | OpenAI GPT-4o |
| Frontend | React 19 + Tailwind CSS + Lucide Icons |

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

| Variable | Description |
|---|---|
| `TAVILY_API_KEY` | Tavily Search API key |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_AGENT_ID` | ElevenLabs Conversational AI agent ID |
| `OPENAI_API_KEY` | OpenAI API key |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio phone number to call from |

## Project Status

🚧 **Scaffolding phase** — Architecture defined, implementation ready to begin.
