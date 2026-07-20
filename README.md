# The Negotiator 🤝

An AI-powered negotiation engine for **residential moving**. Tell it about your
move — by voice or a quick form + document — and it finds real local movers,
calls them, negotiates on your behalf, and hands you a ranked report with a
recommended deal.

## How It Works

```
1. 📝 Intake     → Voice interview (ElevenLabs Agent) or form + document upload
                    (photo/PDF of an existing quote, parsed via OpenAI vision)
2. ✅ Review      → User confirms/corrects the structured job spec before anything is called
3. 🔍 Discover    → Tavily finds real movers near the origin address
                    (phone, address, email, hours — directory pages filtered out)
4. 📞 Call        → ElevenLabs + Twilio place real outbound calls, real-time
                    audio pipeline (Whisper → GPT-4o → ElevenLabs TTS)
5. 🗣️ Negotiate   → The agent negotiates live: cites competing quotes, pushes on fees
6. 💾 Extract     → Each call transcript is turned into a structured, itemized quote
7. 🏆 Rank        → Quotes below 30% of the median get flagged as suspicious, not
                    treated as a win — final report ranks cheapest to most expensive
```

## Architecture

```
Hack_Nation_Negotiator/
├── backend/                    # FastAPI (Python 3.10+)
│   └── app/
│       ├── api/                # specs, search, calls, results — thin routes
│       ├── services/           # search, voice_intake, document_intake, extraction,
│       │                       # ranking, telephony, stream_handler (real-time audio)
│       ├── clients/             # Tavily, ElevenLabs, OpenAI, Twilio wrappers
│       ├── models/              # Pydantic schemas (JobSpec, Lead, Quote, Report)
│       ├── playbook/            # Negotiation tactics as data, not hardcoded prompts
│       └── database.py          # SQLite persistence for call history
└── frontend/                   # React + TanStack Start + Tailwind
    └── src/
        ├── routes/              # /, /start, /voice, /confirm, /calls, /report
        └── components/          # LeafletMap and shared UI
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.10+), SQLite |
| Mover Discovery | Tavily Search API |
| Voice Agents | ElevenLabs Conversational AI |
| Telephony | Twilio (outbound calls + real-time media streams) |
| Intelligence | OpenAI (GPT-4o, Whisper, vision for document intake) |
| Frontend | React + TanStack Start + Tailwind CSS + Framer Motion |

## Getting Started

### Backend

```bash
cd backend
python -m venv venv && source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in a `frontend/.env.local` to point at your backend
(defaults to a shared ngrok tunnel otherwise — override for local testing).

## Environment Variables

See `backend/.env.example` for the full list — key ones:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Extraction, ranking reasoning, document/voice intake parsing |
| `TAVILY_API_KEY` | Mover discovery |
| `ELEVENLABS_API_KEY` | Voice agents |
| `ELEVENLABS_INTAKE_AGENT_ID` | The Estimator agent (voice interview) |
| `ELEVENLABS_CALLER_AGENT_ID` | The Caller agent (negotiates with movers) |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_PHONE_NUMBER` | Outbound calling |
| `DATABASE_URL` | SQLite path for call history persistence |

## Project Status

Backend: job-spec intake (voice, form, document), mover discovery, real-time
Twilio↔ElevenLabs call pipeline, transcript extraction, red-flag ranking, and
SQLite call persistence are all built and tested (86+ backend tests passing).
Frontend covers the full flow from landing page through intake, live calls,
and the final ranked report.
