# LegalCopilot — Architecture

## Overview

LegalCopilot is a two-tier web application. A **Next.js frontend** handles all user interaction and state management. A **FastAPI backend** owns document processing, AI orchestration, and report generation. The two tiers communicate over a REST API; there is no shared database or session store in the current implementation.

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│                                                     │
│   Next.js 14 App (localhost:3000)                   │
│   ┌──────────┐  ┌──────────┐  ┌───────────────┐    │
│   │  Upload  │  │Dashboard │  │ CompareView   │    │
│   │ Section  │  │(results) │  │               │    │
│   └────┬─────┘  └────┬─────┘  └──────┬────────┘    │
│        │             │               │             │
│        └─────────────┴───────────────┘             │
│                      │ Axios (HTTP/JSON)            │
└──────────────────────┼──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│           FastAPI Backend (localhost:8000)          │
│                                                     │
│  /api/analyze  /api/chat  /api/compare  /api/export │
│        │                                            │
│   DocumentService          AIInferenceService       │
│   (PDF extract,            (Claude API +            │
│    text clean)              rule-based fallback)    │
│                                    │                │
└────────────────────────────────────┼────────────────┘
                                     │ HTTPS
                             ┌───────▼────────┐
                             │  Anthropic API │
                             │  Claude Sonnet │
                             └────────────────┘
```

---

## Frontend Architecture

### View State Machine

The root component `page.tsx` is the only stateful page in the app. It holds a `view` discriminated union (`'home' | 'results' | 'compare'`) and conditionally renders one of three top-level components. This keeps routing logic co-located without needing a router library.

```
'home'     →  UploadSection
               │ onAnalysisComplete(result, text)
               ▼
'results'  →  Dashboard
               │ onReset()
               ▼
'home'     (loop)

Header     →  onCompare() sets view = 'compare'
'compare'  →  CompareView
               │ onBack()
               ▼
'home'
```

### Component Tree

```
page.tsx
├── Header
│   └── navigation buttons (Home, Compare)
├── UploadSection                [view = 'home']
│   ├── drag-drop zone (react-dropzone)
│   ├── text paste textarea
│   └── calls analyzeFile() / analyzeText() → api.ts
├── Dashboard                    [view = 'results']
│   ├── RedFlagBanner            (critical clause alert)
│   ├── SummaryPanel             (verdict, key risks, safe aspects)
│   ├── RiskOverview             (score gauge, distribution chart via Recharts)
│   ├── ClauseList               (filterable, expandable clause cards)
│   ├── ChatAssistant            (floating panel, calls sendChatMessage())
│   └── ExportPanel              (calls exportReport())
└── CompareView                  [view = 'compare']
    ├── two UploadSection-like paste areas
    └── comparison table (calls compareDocuments())
```

### API Layer (`src/lib/api.ts`)

All backend communication is centralized in a single module that exports typed async functions. An Axios instance is configured with the base URL from `NEXT_PUBLIC_API_URL` and a 120-second timeout (to accommodate long AI processing). Upload progress is forwarded as 0–30% to leave headroom for the backend processing phase.

---

## Backend Architecture

### Request Lifecycle

```
HTTP Request
     │
     ▼
FastAPI middleware
  └── CORSMiddleware (allows localhost:3000)
     │
     ▼
Router (analyze / chat / compare / export / health)
     │
     ├── DocumentService.extract_text_from_pdf()   [if PDF upload]
     ├── DocumentService.clean_text()
     ├── DocumentService.validate_document()
     │
     ▼
AIInferenceService.analyze_clauses()
     │
     ├── segment_clauses()          ← rule-based text splitting
     │
     ├── analyze_with_claude()      ← async HTTP to Anthropic API
     │       │  (fails / no key)
     │       └── assess_risk_rule_based()  ← keyword fallback
     │
     ├── compute_risk_distribution()
     ├── compute_overall_score()
     └── generate_summary()
     │
     ▼
AnalyzeResponse (Pydantic model)
     │
     ├── stored in document_cache[doc_id]
     └── returned as JSON
```

### Module Responsibilities

**`main.py`** — Application factory. Registers routers, configures CORS, and installs a global exception handler that converts unhandled exceptions to 500 responses without leaking stack traces.

**`routers/analyze.py`** — Handles both multipart file uploads (`POST /analyze`) and JSON text payloads (`POST /analyze/text`). Stores completed analyses in an in-memory dict (`document_cache`) keyed by UUID so that the Chat and Export endpoints can reference the same document.

**`routers/chat.py`** — Accepts a message, optional document context string, and a conversation history list. Sends a focused system prompt plus the last 6 history turns to Claude. Falls back to keyword-matching (`RULE_BASED_RESPONSES`) if the API is unavailable.

**`routers/compare.py`** — Runs `analyze_clauses()` independently on two documents, then computes per-category average risk scores and produces a ranked comparison table sorted by the largest score difference.

**`routers/export.py`** — Accepts an `analysis_data` dict (forwarded from the frontend's copy of the result) and returns either a JSON attachment or a formatted plain-text report.

**`services/ai_service.py`** — Core intelligence layer. Contains the `AIInferenceService` class plus module-level helper functions and lookup tables:

- `RISK_KEYWORDS` — curated keyword lists for each of the four risk levels.
- `CATEGORY_PATTERNS` — keyword lists for each of the 15 clause categories.
- `IMPACT_TEMPLATES` / `generate_explanation()` — deterministic user-facing text for the rule-based path.
- `analyze_with_claude()` — sends up to 20 clauses in one batched prompt, parses the returned JSON array, and maps each element back to the corresponding clause.

**`services/document_service.py`** — Stateless PDF and text utilities. Attempts pdfplumber first, falls back to PyPDF2. `clean_text()` normalises line endings, collapses whitespace, and strips page numbers. `validate_document()` enforces 100-character minimum and 500,000-character maximum.

**`models/schemas.py`** — All Pydantic v2 models. Enums (`RiskLevel`, `ClauseCategory`) are used across both request validation and response serialization, ensuring the frontend and backend share the same vocabulary.

---

## AI Integration

### Clause Analysis

A single call to `analyze_with_claude()` batches up to 20 clauses into one prompt. The system prompt instructs Claude to return a strict JSON array (no prose wrapper), which is then cleaned of any Markdown fences before parsing. Each element is validated against the `AnalyzedClause` schema; any element that fails validation falls back to the rule-based path for that individual clause.

```
System prompt: "Return ONLY a valid JSON array..."
User message:  "Analyze these N legal clauses:\n\nClause 1: ...\n---\nClause 2: ..."

Response:      [ { "category": "...", "risk_level": "High", "risk_score": 72, ... }, ... ]
```

### Risk Scoring

Each clause receives an individual `risk_score` (0–100). The document-level overall score is computed as:

```
overall_score = Σ(clause_score × weight) / Σ(100 × weight)  × 100

weights: Critical = 4, High = 3, Medium = 2, Low = 1
```

This ensures that a document with many Critical clauses scores disproportionately higher than one with the same number of Low clauses.

### Fallback Strategy

Every AI call is wrapped in a try/except. If the call fails (network error, rate limit, missing key, or malformed response), `assess_risk_rule_based()` runs instead. This function scores a clause by counting keyword matches across the four risk-level dictionaries. The frontend is unaware of which path was used; it receives the same `AnalyzedClause` shape regardless, with a lower `confidence` value (0.72 vs 0.85+) for rule-based results.

---

## Data Flow Diagrams

### Document Analysis

```
User drops PDF
      │
      ▼
UploadSection (frontend)
  FormData POST /api/analyze
      │
      ▼
analyze.py router
  ├── extract_text_from_pdf(bytes)
  ├── clean_text(raw)
  └── validate_document(cleaned)
      │
      ▼
AIInferenceService.analyze_clauses(text)
  ├── segment_clauses()  →  [clause_1, clause_2, ... clause_N]
  ├── analyze_with_claude([clause_1..20])
  │       └── httpx POST → api.anthropic.com/v1/messages
  │               └── parse JSON array response
  └── for each clause: build AnalyzedClause (AI result or fallback)
      │
      ▼
compute_risk_distribution()
compute_overall_score()
generate_summary()
      │
      ▼
AnalyzeResponse JSON
  stored in document_cache[doc_id]
      │
      ▼
Dashboard (frontend)
  ├── RiskOverview  ← overall_risk_score, risk_distribution
  ├── SummaryPanel  ← summary.*
  ├── ClauseList    ← clauses[]
  └── ExportPanel   ← full response object
```

### Chat

```
User types question
      │
      ▼
ChatAssistant (frontend)
  POST /api/chat { message, document_context, conversation_history }
      │
      ▼
chat.py router
  ├── query_claude_chat(message, context, history[-6:])
  │       └── httpx POST → api.anthropic.com/v1/messages
  └── (fallback) rule_based_response(message)
      │
      ▼
ChatResponse { response, confidence }
      │
      ▼
ChatAssistant renders assistant bubble
```

---

## Key Design Decisions

**Single-page view state vs. file-based routing** — The app has only three views and no deep-linking requirements. A `useState` enum in `page.tsx` is simpler than Next.js dynamic routes and avoids page reloads that would discard the in-memory analysis result.

**In-memory document cache** — Chosen for simplicity in the current version. The cache uses a UUID key returned to the client, so documents are retrievable within a server session. The comment in `analyze.py` explicitly flags this as a Redis replacement point for production.

**Batched AI analysis** — Sending all clauses in a single prompt (up to 20) instead of one call per clause reduces latency and API cost significantly. The 20-clause cap keeps the prompt within safe token limits while covering the vast majority of real-world T&C documents.

**Dual PDF parser** — pdfplumber is preferred for its layout-aware extraction, but it is a heavier dependency. PyPDF2 is kept as a lightweight fallback. Both are listed in `requirements.txt`.

**Pydantic enums as shared vocabulary** — `RiskLevel` and `ClauseCategory` are defined once in `schemas.py` and re-used everywhere in the backend. The frontend mirrors these as TypeScript string literal types in `types/index.ts`, making the contract explicit without a code-generation step.

**No authentication** — Deliberately omitted in the initial implementation. The architecture comment in `main.py` (`allow_origins=["http://localhost:3000"]`) signals where auth middleware would be inserted before a public deployment.

---

## Identified Extension Points

| Concern | Current State | Production Path |
|---|---|---|
| Document persistence | In-memory dict | Redis / PostgreSQL |
| Authentication | None | FastAPI `Depends` + OAuth2 / API key middleware |
| Rate limiting | None | Starlette `SlowAPI` or reverse-proxy rules |
| PDF OCR | Not supported | Add `pytesseract` + `pdf2image` fallback |
| Streaming responses | Not used | FastAPI `StreamingResponse` + SSE on the frontend |
| Clause cap (50/20) | Hard-coded | Configurable via env var |
| Frontend state | Component `useState` | Zustand / React Context for cross-component sharing |
| Testing | None present | `pytest` + `httpx.AsyncClient` for backend; Playwright for frontend |
