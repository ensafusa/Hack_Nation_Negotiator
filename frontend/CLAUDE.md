# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Hack_Nation_Negotiator — Frontend (React 19)

## Business Purpose

A clean dashboard for the AI negotiation lifecycle.

1. **Search** — Enter a service/location to find providers
2. **Monitor** — Watch AI agents call and negotiate with each provider in real-time
3. **Results** — See the best negotiated price and all provider comparisons

## Tech Stack

- Core: **React 19 (JSX)**
- Styling: **Tailwind CSS**
- Icons: **Lucide React**
- Spinners: **React-Spinners** (or Tailwind-animate spinners)
- API: Axios + WebSockets for live call status updates

## UI/UX Specifics (React 19)

- Use **React 19 Hooks**: `useActionState` for form submissions, `use` for promise handling
- **Loading States**: Every async action must display a Spinner
- **Feedback**: Toast/Alert components for call failures or successful negotiations
- **Real-time Updates**: WebSocket connection for live call status changes

## Screen Architecture

- **Screen 1: Search**
  - Component: `SearchForm.jsx`
  - Input: Service needed + Location
  - Calls `POST /api/search` to find providers
- **Screen 2: Negotiation Monitor**
  - Component: `NegotiationMonitor.jsx`
  - Shows grid of provider cards with live status (Calling/Negotiating/Done/Failed)
  - Icons: `PhoneIncoming`, `CheckCircle`, `AlertTriangle` from Lucide
  - Each card shows the negotiated price once available
- **Screen 3: Results**
  - Component: `BestPrice.jsx`
  - Highlights the best price
  - Shows table of all providers with their negotiated prices

## Coding Standards

- Tailwind for all layout (no CSS files)
- Small, reusable functional components
- Local state for UI; global state via Context API

## Commands

- Run: `npm run dev`
- Install: `npm install`
- Icons: `npm install lucide-react react-spinners`