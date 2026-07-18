# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Hack_Nation_Negotiator — Backend (FastAPI)

## Business Purpose

An AI negotiation engine that searches for home improvement ("aménagement") providers, calls them via AI voice agents, negotiates pricing, and returns the best deal to the user.

### Core Flow

1. **Search** — Tavily API finds providers (phone numbers extracted from results)
2. **Call & Negotiate** — ElevenLabs Conversational AI calls each provider and negotiates the price
3. **Extract & Store** — The final negotiated price is extracted from the call transcript and stored in memory
4. **Compare & Return** — After all calls complete, the best price is returned to the user

## Tech Stack

- Framework: FastAPI (Python 3.10+)
- Provider Discovery: Tavily Search API
- Voice Negotiation: ElevenLabs Conversational AI + Twilio
- Intelligence: OpenAI GPT-4o for transcript extraction
- Architecture: Strict SRP (Single Responsibility Principle)

## Directory & Responsibility Map

```
backend/
├── app/
│   ├── main.py              # Entry point: app init & routing
│   ├── config.py             # Central config (API keys, thresholds)
│   ├── api/
│   │   ├── search.py         # POST /api/search — find providers
│   │   ├── negotiate.py      # POST /api/negotiate — start batch calls
│   │   └── results.py        # GET /api/results — get best price
│   ├── services/
│   │   ├── search_service.py # Tavily search + phone extraction logic
│   │   ├── voice_service.py  # ElevenLabs agent prompt orchestration
│   │   ├── telephony.py      # Twilio stream handling & call bridging
│   │   ├── extraction.py     # Transcript-to-price extraction (OpenAI)
│   │   └── memory.py         # In-memory store of negotiated prices
│   ├── clients/
│   │   ├── tavily_client.py  # Tavily API wrapper
│   │   ├── eleven_client.py  # ElevenLabs API wrapper
│   │   ├── openai_client.py  # OpenAI API wrapper
│   │   └── twilio_client.py  # Twilio API wrapper
│   └── models/
│       └── schemas.py        # Pydantic models (Provider, NegotiationResult, etc.)
```

### File Responsibilities

- **clients/**: Thin, vendor-specific SDK wrappers. No business logic.
- **services/search_service.py**: Takes a query/location, uses Tavily client, extracts phone numbers via regex/LLM, returns clean providers.
- **services/voice_service.py**: Builds the ElevenLabs agent prompt with the negotiation context (what service, target price range).
- **services/telephony.py**: Bridges Twilio call audio to the ElevenLabs agent. Only cares about stream health.
- **services/extraction.py**: After a call ends, takes the transcript and asks OpenAI to extract the final negotiated price as structured JSON.
- **services/memory.py**: Simple in-memory store mapping provider -> negotiated price. Gets queried after all calls complete.
- **api/**: Thin route handlers — validate request, call service, return response.

## Coding Standards

- Async/Await: Required for all external API calls
- Schema: Strict Pydantic models for all data
- Config: Never hardcode API keys or thresholds; use `config.py`

## Commands

- Run: `uvicorn app.main:app --reload`
- Install: `pip install -r requirements.txt`