# LegalCopilot

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688) ![License](https://img.shields.io/badge/license-MIT-blue)

**AI-powered Terms & Conditions risk analyzer.** LegalCopilot parses legal documents, identifies risky clauses, scores overall risk, and lets users ask plain-language questions about what they're agreeing to — before they click "I Accept."

---

## Live Demo

> Local deployment only at this time. Follow the [Quick Start](#quick-start) guide to run the app on your machine.
>
> Hosted demo — coming soon.

---

## Features

- **Document Analysis** — Upload a PDF or paste raw text; the app segments the document into clauses and assigns each a risk level (Low / Medium / High / Critical) and a 0–100 risk score.
- **Risk Dashboard** — Visual summary showing overall risk score, risk distribution chart, red-flag banner, clause list, and a plain-English verdict.
- **AI Chat Assistant** — Ask questions about the document in natural language. Powered by Claude with a keyword-based fallback when the API is unavailable.
- **Document Comparison** — Paste two T&C documents side-by-side and get a category-by-category breakdown of which is safer.
- **Export** — Download the full analysis as a JSON data file or a human-readable `.txt` report.
- **Graceful Degradation** — Every AI call has a deterministic rule-based fallback, so the app works even without an Anthropic API key.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Charts | Recharts |
| Animations | Framer Motion |
| HTTP client (frontend) | Axios |
| File upload | react-dropzone |
| Backend | FastAPI, Python 3.10+, Uvicorn |
| AI Engine | Anthropic Claude (`claude-sonnet-4-20250514`) with rule-based fallback |
| PDF parsing | pdfplumber (primary), PyPDF2 (fallback) |
| Data validation | Pydantic v2 |

---

## AI Model

LegalCopilot uses a **two-tier inference strategy** so the app remains functional with or without an API key:

| Tier | Engine | When Used |
|---|---|---|
| **Primary** | Anthropic Claude `claude-sonnet-4-20250514` | When `ANTHROPIC_API_KEY` is set and the API is reachable |
| **Fallback** | Rule-based keyword engine | API unavailable, rate-limited, or key not configured |

The rule-based fallback covers 50+ curated risk keywords across four severity levels and 15 legal clause categories. Clauses analysed via fallback return a lower `confidence` score (0.72 vs 0.85+) so the frontend can surface the distinction if needed.

---

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- An **Anthropic API key** (optional — the app runs with rule-based analysis without it)

---

## Quick Start

### Automated setup

```bash
# macOS / Linux
chmod +x setup.sh && ./setup.sh

# Windows
setup.bat
```

### Manual setup

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

python main.py
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/api/docs
```

**Frontend**

```bash
cd frontend
npm install
# .env.local already points to http://localhost:8000/api
npm run dev
# App available at http://localhost:3000
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | No | `""` | Enables AI-powered clause analysis and chat |
| `HOST` | No | `0.0.0.0` | Uvicorn bind address |
| `PORT` | No | `8000` | Uvicorn port |
| `RELOAD` | No | `true` | Hot-reload on file changes |
| `LOG_LEVEL` | No | `info` | Logging verbosity |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api` | Backend base URL |

---

## API Reference

Full interactive docs are available at `http://localhost:8000/api/docs` when the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/analyze` | Analyze a PDF or text file (multipart) |
| `POST` | `/api/analyze/text` | Analyze raw JSON text body |
| `GET` | `/api/document/{doc_id}` | Retrieve cached analysis by ID |
| `POST` | `/api/chat` | Chat with AI about a document |
| `POST` | `/api/compare` | Compare two documents |
| `POST` | `/api/export` | Export report as JSON or plain text |

---

## How Analysis Works

1. **Ingestion** — Text is extracted from the uploaded file (PDF via pdfplumber/PyPDF2, plain text directly) and cleaned (whitespace normalization, page-number stripping).
2. **Segmentation** — The document is split into clauses using numbered-section patterns, paragraph breaks, or sentence chunking as fallbacks.
3. **AI Analysis** — Up to 20 clauses are sent to Claude in one batch with a structured prompt requesting category, risk level, risk score, plain-English impact, explanation, and red flags.
4. **Rule-based Fallback** — If the Claude API is unavailable or returns no result for a clause, keyword matching against curated risk dictionaries assigns category and risk level.
5. **Scoring** — An overall score is computed as a weighted average of individual clause scores, with Critical clauses weighted 4× and Low clauses weighted 1×.
6. **Caching** — Completed analyses are stored in an in-memory dict keyed by UUID, enabling the Chat and Export features to reference the same document without re-analysis.

---

## Supported File Types

- `.pdf` — Parsed with pdfplumber; falls back to PyPDF2
- `.txt` — UTF-8 plain text
- `.md` — Markdown (treated as plain text)

Maximum document size: **500,000 characters**.

---

## Project Structure

```
legalcopilot/
├── backend/
│   ├── main.py                  # FastAPI app, middleware, router registration
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── analyze.py           # Document ingestion & analysis endpoints
│   │   ├── chat.py              # Conversational Q&A endpoint
│   │   ├── compare.py           # Side-by-side document comparison
│   │   ├── export.py            # Report download (JSON / TXT)
│   │   └── health.py            # Health check
│   ├── services/
│   │   ├── ai_service.py        # Claude API calls + rule-based fallback
│   │   └── document_service.py  # PDF extraction, text cleaning, validation
│   └── utils/
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── app/
│       │   ├── page.tsx         # Root page, view state machine
│       │   ├── layout.tsx
│       │   └── globals.css
│       ├── components/
│       │   ├── Header.tsx
│       │   ├── upload/          # UploadSection (drag-drop + paste)
│       │   ├── dashboard/       # Dashboard, RiskOverview, SummaryPanel, RedFlagBanner
│       │   ├── clauses/         # ClauseList
│       │   ├── chat/            # ChatAssistant
│       │   ├── comparison/      # CompareView
│       │   └── export/          # ExportPanel
│       ├── lib/
│       │   └── api.ts           # Typed Axios wrappers for all endpoints
│       └── types/
│           └── index.ts         # Shared TypeScript interfaces and enums
├── setup.sh
├── setup.bat
└── README.md
```

---

## Limitations & Production Notes

- **In-memory document cache** — Analyzed documents are stored in a Python dict. Data is lost on restart. For production, replace with Redis or a database.
- **No authentication** — The API has no auth layer. Add OAuth2 or API key middleware before any public deployment.
- **CORS** — Currently allows only `localhost:3000`. Update `allow_origins` in `main.py` for your production domain.
- **Clause cap** — A maximum of 50 clauses are segmented per document and 20 are sent to Claude per request. Very long documents may have lower coverage.
- **Not legal advice** — LegalCopilot is an educational tool. It does not constitute legal advice and should not be used as a substitute for qualified legal counsel.

---

## License

See `LICENSE` for terms.
