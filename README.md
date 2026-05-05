# Resume Analyzer Pro

AI-powered resume analysis, job matching, and recruiter-side screening — built with FastAPI and Groq.

Two flows in one app:

- **Candidate flow** — upload a PDF resume and get structured extraction, career analysis, ATS compatibility scoring, job recommendations, and an AI chat about your profile.
- **Recruiter flow** — upload many resumes against a job spec, get them ranked with skill-match breakdowns and gaps.

## Quick Start

```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
python main.py
```

Open http://localhost:8000.

> Get a free Groq API key at [console.groq.com](https://console.groq.com).

## Features

**Candidate side**
- Drag-and-drop PDF resume upload with inline progress + toast notifications
- Structured extraction (skills, experience, education, contact)
- AI career analysis: trajectory, strengths, gaps, industry fit, suggested job summary
- ATS compatibility check against any job description (Workday, Taleo, iCIMS, Greenhouse, Lever, BambooHR, or generic)
- Targeted ATS improvement suggestions (keywords / format / structure)
- Job recommendations with match scores
- LinkedIn profile merge (Selenium-based, optional)
- AI chat about your resume

**Recruiter side**
- Single-resume parsing with structured extraction
- Single-candidate scoring against job requirements
- Batch screening of up to 50 resumes
- Side-by-side comparison of 2–5 candidates
- Job-requirements template endpoint

**Standalone**
- Job description analyzer (no resume needed)
- Market insights: salary ranges, demand, top skills, career paths

## Technical Stack

- **Backend**: FastAPI 0.115, Python 3.12, gunicorn + uvicorn workers in production
- **AI**: Groq API (default model: `openai/gpt-oss-120b`, configurable)
- **PDF**: pypdf
- **Scraping**: Selenium (LinkedIn merge)
- **Sessions**: in-memory (default) or Redis (multi-worker)
- **Rate limiting**: slowapi
- **Logging**: stdlib `logging`, JSON-formatted in production via `python-json-logger`
- **Frontend**: vanilla HTML/CSS/JS — no framework. Uses Inter (body) + Space Grotesk (display)

## Requirements

- Python 3.12 (3.10+ should work)
- Groq API key
- For the LinkedIn merge feature: Chrome + a matching ChromeDriver on PATH
- For multi-worker production: Redis 5+

## Installation

### conda (used in development)

```bash
conda activate main
pip install -r requirements.txt
cp .env.example .env   # then edit GROQ_API_KEY
python main.py
```

### venv

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # edit GROQ_API_KEY
python main.py
```

## Configuration

Copy `.env.example` to `.env`. All settings have sensible defaults except `GROQ_API_KEY`.

```env
# Required
GROQ_API_KEY=your_groq_api_key

# Model
GROQ_MODEL=openai/gpt-oss-120b

# Environment
ENV=development                # "development" | "production"
LOG_LEVEL=INFO
LOG_JSON=false                 # true in prod for structured logs

# Sessions
SESSION_BACKEND=memory         # "memory" | "redis"
SESSION_TIMEOUT=3600           # seconds (idle TTL)
SESSION_CLEANUP_INTERVAL=300   # background sweep interval
REDIS_URL=redis://localhost:6379/0

# Limits
MAX_FILE_SIZE=10485760         # 10 MB
REQUEST_TIMEOUT=60             # per-LLM-call

# Rate limiting (slowapi syntax)
RATE_LIMIT_DEFAULT=60/minute
RATE_LIMIT_UPLOAD=10/minute
RATE_LIMIT_LLM=30/minute

# CORS — comma-separated origins; blank disables CORS middleware
CORS_ORIGINS=
```

## Production Deployment

### Single host (gunicorn)

```bash
ENV=production LOG_JSON=true gunicorn -c gunicorn_conf.py main:app
```

By default this spawns `(2 × CPU) + 1` workers.

> ⚠️ **If you run more than one worker, set `SESSION_BACKEND=redis`.** The default
> in-memory session store is per-process; without Redis, users will lose their
> session randomly between requests as the load balancer round-robins them.

### Docker

```bash
docker build -t resume-summarizer .
docker run --rm -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e SESSION_BACKEND=redis \
  -e REDIS_URL=redis://host:6379/0 \
  resume-summarizer
```

The image runs as non-root `appuser`, exposes 8000, and uses
`gunicorn_conf.py` as the entrypoint. JSON logs are enabled by default in the image.

### Production checklist

- [ ] `ENV=production` (hides `/docs` and `/redoc`)
- [ ] `SESSION_BACKEND=redis` if `WEB_CONCURRENCY > 1`
- [ ] `LOG_JSON=true`
- [ ] `CORS_ORIGINS` set to your frontend origins
- [ ] Reverse proxy (nginx/Caddy) terminating TLS
- [ ] Rate limits tuned to your traffic shape

## Project Structure

```
resume-summarizer/
├── app/                       # Web layer
│   ├── config.py              # env-driven config + tokens
│   ├── errors.py              # safe HTTP error helpers
│   ├── handlers.py            # Resume/Chat/LinkedIn/Job handlers
│   ├── logging_config.py      # JSON or plain stdlib logging
│   ├── models.py              # Pydantic request models
│   ├── screening_handlers.py  # Recruiter screening handlers
│   ├── screening_routes.py    # /screening/* APIRouter
│   ├── services.py            # PDF + LLM integration
│   └── session_manager.py     # Memory + Redis backends
├── src/                       # Domain modules
│   ├── builders/              # ProfileBuilder (resume + LinkedIn merge)
│   ├── parsers/               # ResumeParser, BatchScreeningSystem
│   ├── recommenders/          # JobRecommender
│   ├── scrapers/              # LinkedInScraper (Selenium)
│   └── utils/                 # ATSChecker, PDF QA
├── static/                    # Frontend (vanilla HTML/CSS/JS)
│   ├── index.html             # Upload page
│   ├── analysis.html          # Analysis results
│   ├── jobs.html              # Standalone job tools
│   ├── screening.html         # Recruiter batch screening
│   ├── style.css              # Base styles
│   ├── motion.css             # Animations + interactions
│   ├── theme.css              # Arc/Apple-inspired theme overlay
│   ├── motion.js              # Toasts, drag/drop, scroll reveal, ripple
│   ├── script.js              # Upload page logic
│   ├── analysis.js            # Analysis page logic
│   ├── jobs.js                # Jobs page logic
│   └── screening.js           # Screening page logic
├── tests/                     # pytest suite
├── docs/                      # Project documentation
├── main.py                    # FastAPI entrypoint with lifespan
├── gunicorn_conf.py           # Production server config
├── Dockerfile                 # Production image
├── .dockerignore
├── .env.example               # Config template
└── requirements.txt
```

## API Reference

### Candidate flow

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/upload` | multipart `file`, `session_id` | Upload + parse resume |
| POST | `/get-analysis` | `{session_id}` | Detailed AI career analysis |
| POST | `/chat` | `{session_id, message}` | Chat about the resume |
| POST | `/add-linkedin` | `{session_id, linkedin_url}` | Merge LinkedIn data |
| POST | `/skip-linkedin` | `{session_id}` | Build profile from resume only |
| POST | `/recommend-jobs` | `{session_id}` | Personalized job matches |
| POST | `/check-ats` | form: `session_id`, `job_description`, `target_role?`, `ats_system?` | ATS compatibility score |
| POST | `/ats-suggestions` | `{session_id, improvement_type}` | Targeted improvement tips |

### Standalone

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/analyze-job` | form: `job_description`, `target_role?`, `analysis_type?` | Analyze a JD without a resume |
| POST | `/market-insights` | form: `job_role`, `experience_level?`, `industry?`, `location?` | Salary + demand insights |

### Recruiter screening

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/screening/parse-resume` | multipart `file` | Parse one resume |
| POST | `/screening/screen-candidate` | multipart `file`, form `job_requirements` (JSON) | Score one candidate |
| POST | `/screening/screen-batch` | multipart `files[]`, form `job_requirements` | Rank up to 50 candidates |
| POST | `/screening/compare-candidates` | multipart `files[]`, form `job_requirements` | Side-by-side compare |
| GET  | `/screening/job-requirements-template` | – | Sample requirements JSON |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/docs` | OpenAPI UI (dev only) |

## Workflows

### As a candidate

1. Drop a PDF resume on the upload card → analysis runs in ~5–10 seconds
2. Auto-redirect to `/analysis.html` shows extracted profile + AI analysis
3. Optionally add a LinkedIn URL to enrich the data
4. Click **Generate Job Recommendations** for matched roles
5. Use the chat fab to ask the AI questions about your profile
6. Optionally run **Check ATS** with a target job description for an ATS score

### As a recruiter

1. Open `/screening.html`
2. Step 1 — define the role: title, required + preferred skills, experience range, degree
3. Step 2 — upload up to 50 candidate PDFs
4. Step 3 — review ranked candidates with skill match breakdowns

### Best practices

- Use text-based PDFs (selectable text, not scanned images)
- Include complete work history with dates
- For ATS checks, paste the *full* job description, not just the title

## Frontend

The UI is vanilla HTML/CSS/JS with three layered stylesheets and a single
interaction script:

- **`style.css`** — base layout, components, original token system
- **`motion.css`** — animations, transitions, toast styles, skeleton loaders, drag-and-drop visuals
- **`theme.css`** — current redesign: glass cards, mesh-gradient background, deep navy hero, Space Grotesk display type, eyebrow labels on section headers
- **`motion.js`** — scroll reveal, navbar elevation, ripple, count-up, drag-and-drop wiring, clipboard, toast API (`window.UI.toast()`)

All animation respects `prefers-reduced-motion`.

## Troubleshooting

**`GROQ_API_KEY not found in .env file`**
Make sure `.env` exists in the project root and contains a valid key.

**Port 8000 already in use**
Either kill the existing process or pass a different port:
`uvicorn main:app --port 8001`.

**`Failed to extract text from PDF`**
The file is a scanned image. Use a text-based PDF or run OCR first.

**Session expired / "No resume uploaded for this session"**
Sessions live 1 hour by default (`SESSION_TIMEOUT`). Re-upload, or increase the value.

**LinkedIn extraction fails**
Selenium needs Chrome + a matching chromedriver. The app falls back to
"resume-only" automatically — no hard failure.

**Multi-worker session loss in production**
You're hitting different workers between requests. Set `SESSION_BACKEND=redis`.

### Logs

Plain text in development; structured JSON when `LOG_JSON=true`. Useful fields:
`incident_id`, `session`, `error`. Each 5xx response includes the incident id
in `detail` so you can correlate.

## Security

- API keys live in `.env` only (excluded from Docker via `.dockerignore`)
- File uploads validated by extension and 10 MB cap (`MAX_FILE_SIZE`)
- Session ids strictly validated (`^[A-Za-z0-9_-]{8,128}$`)
- Per-IP rate limiting on every endpoint
- HTTP error responses don't leak `str(exception)` — incidents are logged with a UUID and the client gets a generic message + that UUID
- Hidden `/docs` in production (`ENV=production`)

> Sessions are still **client-id-supplied** (the frontend generates a session id
> and passes it on every request). For higher-security deployments, switch to
> server-issued, httpOnly-cookie sessions before exposing this publicly.

## Development

### Tests

```bash
pytest tests/
```

### Style

```bash
black app/ src/
pylint app/ src/
```

### Adding endpoints

1. Add request schema to `app/models.py`
2. Add a method to the right handler class in `app/handlers.py` (or a new one)
3. Wire it into `main.py` with a `@limiter.limit(...)` rate cap
4. Update this README's API table

## Contributing

1. Fork
2. `git checkout -b feature/your-thing`
3. Add tests
4. `pytest tests/` + `black .`
5. Open a PR

## Changelog

### 1.1.0 (current)

**Backend hardening (production-ready)**
- Resolved `requirements.txt` merge conflict; added `gunicorn`, `slowapi`, `redis`, `python-json-logger`
- Switched `PyPDF2` → `pypdf`
- New: pluggable `SessionManager` with in-memory + Redis backends, thread-safe, background cleanup task
- New: `errors.py` — incident-id'd safe HTTP errors (no `str(e)` leakage)
- New: `logging_config.py` — JSON in prod, plain in dev
- New: rate limiting via `slowapi` on every endpoint, per-route caps
- Singleton `JobRecommender` and `ATSChecker` in app `lifespan` (no per-request construction)
- `FileResponse` for HTML routes (proper caching headers, mime types)
- Strict `session_id` validation (regex, 8–128 chars)
- Replaced hardcoded fake market/job analysis stubs with real LLM calls
- New `Dockerfile`, `.dockerignore`, `gunicorn_conf.py`, `.env.example`

**Frontend redesign**
- New `theme.css` — Arc/Apple-inspired glass system, deep navy hero, mesh-gradient body, Space Grotesk display type
- Eyebrow labels + gradient titles on section headers across all pages
- Bento grid for "How it works"
- Inline upload progress (replaces full-screen overlay)
- Drag-and-drop on upload card with live state machine
- Toast system (`window.UI.toast()`) replaces all `alert()` calls
- Scroll-reveal, ripple buttons, conic-gradient card halo on hover
- Click-to-copy email on profile, count-up animations on stats
- Slim glass navbar + slim 1-line footer
- All motion respects `prefers-reduced-motion`

### 1.0.0

- Initial release
- Resume upload and analysis
- AI-powered career insights
- Job recommendations
- LinkedIn integration
- Interactive chat assistant

---

Built with FastAPI + Groq. Frontend in vanilla HTML/CSS/JS.
