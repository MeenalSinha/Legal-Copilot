# LegalCopilot — AI-Powered Terms & Conditions Analyzer

A production-grade legal AI system that analyzes Terms & Conditions and Privacy Policies at clause level, detects risks, explains complex legal language, and provides structured visual insights.

---

## Folder Structure

```
legalcopilot/
├── backend/                          # FastAPI Python backend
│   ├── main.py                       # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   ├── routers/
│   │   ├── analyze.py                # POST /api/analyze — core analysis
│   │   ├── chat.py                   # POST /api/chat — AI assistant
│   │   ├── compare.py                # POST /api/compare — document comparison
│   │   ├── export.py                 # POST /api/export — report generation
│   │   └── health.py                 # GET /api/health — health check
│   ├── services/
│   │   ├── ai_service.py             # AI inference engine (Claude + rule-based)
│   │   └── document_service.py       # PDF parsing and text processing
│   └── models/
│       └── schemas.py                # Pydantic request/response models
│
├── frontend/                         # Next.js React frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Root page — view controller
│   │   │   ├── layout.tsx            # HTML layout with fonts
│   │   │   └── globals.css           # Global styles + CSS variables
│   │   ├── components/
│   │   │   ├── Header.tsx            # Top navigation bar
│   │   │   ├── upload/
│   │   │   │   └── UploadSection.tsx # File upload + text paste UI
│   │   │   ├── dashboard/
│   │   │   │   ├── Dashboard.tsx     # Main results orchestrator
│   │   │   │   ├── RiskOverview.tsx  # Charts, gauge, timeline
│   │   │   │   ├── SummaryPanel.tsx  # AI verdict + key risks
│   │   │   │   └── RedFlagBanner.tsx # Critical alert banner
│   │   │   ├── clauses/
│   │   │   │   └── ClauseList.tsx    # Filtered clause cards
│   │   │   ├── chat/
│   │   │   │   └── ChatAssistant.tsx # AI chat interface
│   │   │   ├── comparison/
│   │   │   │   └── CompareView.tsx   # Two-doc comparison
│   │   │   └── export/
│   │   │       └── ExportPanel.tsx   # Download reports
│   │   ├── lib/
│   │   │   └── api.ts                # API client (axios)
│   │   └── types/
│   │       └── index.ts              # TypeScript types
│   ├── package.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── tsconfig.json
│   └── .env.local
│
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- An Anthropic API key (get one free at https://console.anthropic.com)

---

### Step 1: Backend Setup

```bash
cd legalcopilot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# OR: venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Start the server
python main.py
# OR: uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/api/docs

---

### Step 2: Frontend Setup

```bash
cd legalcopilot/frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend runs at: http://localhost:3000

---

## Features

### Core Analysis
- Upload PDF or paste text
- AI-powered clause segmentation and analysis
- Risk scoring (0–100) per clause and overall
- Risk levels: Low, Medium, High, Critical
- 15 legal category classifications
- AI confidence scoring

### Risk Dashboard
- Visual risk score gauge
- Pie chart — risk distribution
- Bar chart — risk by category
- Timeline view — risk through document

### Clause Viewer
- All clauses with expandable details
- Filter by risk level
- Search by content or category
- Red flag phrase highlighting
- Plain-language explanations
- User impact statements

### AI Chat Assistant
- Ask questions about the document
- Powered by Claude API with rule-based fallback
- Conversation history maintained
- Suggested questions provided

### Document Comparison
- Compare two T&C documents side-by-side
- Score comparison with winner declaration
- Category-level breakdown
- Detailed verdict explanation

### Export
- JSON report download (client-side)
- Text report via backend API
- REST API for integration

### Red Flag Detection
- Critical alert banner for dangerous documents
- Specific red flag phrase extraction
- "Most dangerous clauses" section

---

## API Reference

### POST /api/analyze
Upload a file or form-post text for analysis.

**Form fields:**
- `file` (optional): PDF, TXT, or MD file
- `text` (optional): Raw text string
- `document_name` (optional): Display name

**Response:**
```json
{
  "document_id": "uuid",
  "overall_risk_score": 72,
  "risk_distribution": { "low": 3, "medium": 4, "high": 5, "critical": 2 },
  "clauses": [
    {
      "id": "uuid",
      "text": "...",
      "category": "Data Sharing",
      "risk_level": "High",
      "risk_score": 68,
      "user_impact": "Your data may be shared with advertisers.",
      "explanation": "...",
      "confidence": 0.91,
      "red_flags": ["share with advertisers"]
    }
  ],
  "summary": {
    "overall_risk_score": 72,
    "risk_level": "High",
    "key_risks": ["..."],
    "user_rights": ["..."],
    "verdict": "...",
    "red_flag_count": 7
  },
  "processing_time": 2.4
}
```

### POST /api/chat
```json
{
  "message": "Can they sell my data?",
  "document_context": "optional summary",
  "conversation_history": []
}
```

### POST /api/compare
```json
{
  "document_a_text": "...",
  "document_b_text": "...",
  "document_a_name": "Google ToS",
  "document_b_name": "Apple ToS"
}
```

### POST /api/export
```json
{
  "analysis_data": { ... },
  "format": "json"
}
```

---

## AI Architecture

```
User Input (PDF / Text)
        |
        v
Document Service (PDF parsing, text cleaning)
        |
        v
Clause Segmentation (regex + NLP heuristics)
        |
        v
AI Inference Service
  ├── Primary: Anthropic Claude API (claude-sonnet-4)
  │     └── Returns: category, risk_level, risk_score,
  │                  user_impact, explanation, red_flags, confidence
  └── Fallback: Rule-based keyword engine
        └── Pattern matching on 50+ legal risk keywords
        |
        v
Risk Aggregation + Summary Generation
        |
        v
Structured JSON Response → Frontend
```

---

## Design System

- **Colors**: Light theme — white/light grey base, high-contrast text
- **Typography**: DM Sans (body), DM Serif Display (headings), DM Mono (code)
- **Risk Colors**: Green (#16a34a) Low | Amber (#b45309) Medium | Red (#dc2626) High | Dark Red (#7c2d12) Critical
- **No dark mode** — clean professional light interface throughout

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, TypeScript |
| Styling | Tailwind CSS, CSS Variables |
| Charts | Recharts |
| Icons | Lucide React |
| HTTP | Axios |
| File Upload | React Dropzone |
| Toasts | React Hot Toast |
| Backend | FastAPI (Python) |
| AI | Anthropic Claude API |
| PDF Parsing | pdfplumber |
| Validation | Pydantic v2 |
| HTTP Client | httpx (async) |

---

## Production Notes

- Replace in-memory `document_cache` in `analyze.py` with Redis
- Add authentication middleware for multi-user deployments
- Rate limit the `/api/analyze` endpoint
- Use environment-based CORS origins
- Set up PostgreSQL for persistent analysis history
- Add Sentry for error monitoring
