# Resume Analyzer Pro

AI-powered resume analysis, job intelligence, and recruiter-side screening. Built with FastAPI and Groq.

> **Just want to run it?** See [QUICKSTART.md](QUICKSTART.md) — three commands, two minutes.

---

## What it does

Two flows in one app:

**Candidate flow.** Upload a PDF resume → get structured extraction (skills, experience, education) → AI career analysis → ATS compatibility scoring → matched job recommendations → an AI chat about your profile. Optional LinkedIn enrichment via paste or Selenium scrape.

**Recruiter flow.** Define a job spec → upload up to 50 candidate PDFs → get them ranked with skill-match breakdowns and gaps. Side-by-side comparison of 2-5 candidates also available.

Plus standalone job-tools (analyze any JD, get market insights for any role) that don't need a resume.

---

## Tech stack

- **Backend** — FastAPI 0.115, Python 3.12, gunicorn + uvicorn workers in production
- **AI** — Groq API (default model `openai/gpt-oss-120b`, configurable)
- **PDF** — `pypdf`
- **LinkedIn** — paste-text (LLM extraction) primary, Selenium scrape fallback
- **Sessions** — in-memory (dev) or Redis (multi-worker prod)
- **Rate limiting** — `slowapi`
- **Logging** — stdlib `logging`, JSON-formatted in production via `python-json-logger`
- **Observability** — optional Sentry + Prometheus `/metrics`
- **Static assets** — minified + content-hashed in production (no build step, pure Python)
- **Frontend** — vanilla HTML/CSS/JS with three layered stylesheets, no framework

---

## Requirements

- Python 3.12 (3.10+ should work)
- Groq API key — free tier at [console.groq.com](https://console.groq.com)
- Chrome + matching chromedriver (only for the Selenium LinkedIn scrape; paste-LinkedIn doesn't need it)
- Redis 5+ (only for multi-worker production)

---

## Setup

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
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
cp .env.example .env           # edit GROQ_API_KEY
python main.py
```

Open http://localhost:8000.

---

## Configuration

Copy `.env.example` to `.env`. Everything has sensible defaults except `GROQ_API_KEY`.

```env
# Required
GROQ_API_KEY=your_groq_api_key

# Model + env
GROQ_MODEL=openai/gpt-oss-120b
ENV=development                # "development" | "production"
LOG_LEVEL=INFO
LOG_JSON=false                 # true in prod for structured logs

# Sessions
# Use "redis" in production (required if WEB_CONCURRENCY > 1). "memory" is dev-only.
SESSION_BACKEND=memory
SESSION_TIMEOUT=3600
SESSION_CLEANUP_INTERVAL=300
REDIS_URL=redis://localhost:6379/0

# Limits
MAX_FILE_SIZE=10485760         # 10 MB
REQUEST_TIMEOUT=60             # seconds per LLM call

# Rate limiting (slowapi syntax)
RATE_LIMIT_DEFAULT=60/minute
RATE_LIMIT_UPLOAD=10/minute
RATE_LIMIT_LLM=30/minute

# CORS — comma-separated origins; blank disables CORS middleware
CORS_ORIGINS=

# Error tracking (optional)
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.05
SENTRY_PROFILES_SAMPLE_RATE=0.0

# Prometheus metrics (optional)
METRICS_ENABLED=false
METRICS_BASIC_AUTH=            # e.g. "user:pass" to require basic auth on /metrics
```

---

## Production Deployment

### gunicorn on a single host

```bash
ENV=production LOG_JSON=true gunicorn -c gunicorn_conf.py main:app
```

By default this spawns `(2 × CPU) + 1` workers.

> **If you run more than one worker, set `SESSION_BACKEND=redis`.** The default in-memory
> session store is per-process; without Redis, users will lose their session randomly
> between requests as the load balancer round-robins them.

### docker compose (app + Redis)

```bash
cp .env.example .env   # edit GROQ_API_KEY
docker compose up --build
```

The compose file boots the app with `ENV=production`, `LOG_JSON=true`, `SESSION_BACKEND=redis`,
`WEB_CONCURRENCY=4`, and a persistent Redis volume. Health check on Redis blocks the app from
starting until Redis is ready.

### Plain docker

```bash
docker build -t resume-summarizer .
docker run --rm -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e SESSION_BACKEND=redis \
  -e REDIS_URL=redis://host:6379/0 \
  resume-summarizer
```

The image runs as non-root `appuser`, exposes 8000, and uses `gunicorn_conf.py` as entrypoint.
JSON logs are on by default in the image.

### Production checklist

- [ ] `ENV=production` (hides `/docs` and `/redoc`)
- [ ] `SESSION_BACKEND=redis` if `WEB_CONCURRENCY > 1`
- [ ] `LOG_JSON=true`
- [ ] `CORS_ORIGINS` set to your frontend origins
- [ ] Reverse proxy (nginx/Caddy) terminating TLS
- [ ] `SENTRY_DSN` set if you want error aggregation
- [ ] `METRICS_ENABLED=true` (+ `METRICS_BASIC_AUTH`) if you want Prometheus scraping
- [ ] Rate limits tuned to your traffic shape

---

## Project structure

```
resume-summarizer/
├── app/                          # Web layer (FastAPI)
│   ├── config.py                 # env-driven config + tokens
│   ├── errors.py                 # safe HTTP error helpers
│   ├── handlers.py               # Resume/Chat/LinkedIn/Job handlers
│   ├── health.py                 # /health probes (Redis + Groq)
│   ├── logging_config.py         # stdlib logging, JSON in prod
│   ├── models.py                 # Pydantic request models
│   ├── observability.py          # optional Sentry + Prometheus init
│   ├── screening_handlers.py     # recruiter screening handlers
│   ├── screening_routes.py       # /screening/* APIRouter
│   ├── services.py               # PDF + LLM integration
│   ├── session_manager.py        # in-memory + Redis backends
│   └── static_manifest.py        # minify + content-hash static assets (prod)
├── src/                          # Domain modules
│   ├── _logprint.py              # routes legacy print() to logging
│   ├── builders/                 # ProfileBuilder (resume + LinkedIn merge)
│   ├── parsers/                  # ResumeParser, BatchScreeningSystem
│   ├── recommenders/             # JobRecommender
│   ├── scrapers/                 # LinkedInScraper (Selenium)
│   └── utils/                    # ATSChecker, PDF QA
├── static/                       # Frontend (vanilla HTML/CSS/JS)
│   ├── index.html                # upload page
│   ├── analysis.html             # results page (with sticky TOC rail)
│   ├── jobs.html                 # standalone job tools
│   ├── screening.html            # recruiter batch screening
│   ├── style.css                 # base layout + components
│   ├── motion.css                # animations, toasts, skeletons
│   ├── theme.css                 # corporate/enterprise theme overlay
│   ├── motion.js                 # toasts, drag/drop, scroll reveal, TOC, ripple
│   ├── script.js                 # upload page logic
│   ├── analysis.js               # analysis page logic
│   ├── jobs.js                   # jobs page logic
│   └── screening.js              # screening page logic
├── tests/                        # pytest suite (24 tests)
├── docs/                         # additional documentation
├── main.py                       # FastAPI entrypoint with lifespan
├── gunicorn_conf.py              # production server config
├── docker-compose.yml            # app + Redis
├── Dockerfile
├── .dockerignore
├── .env.example                  # config template
└── requirements.txt
```

---

## API Reference

Explore the live OpenAPI at http://localhost:8000/docs (dev only; hidden in production).

### Candidate flow

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/upload` | multipart `file`, `session_id` | Upload + parse resume PDF |
| POST | `/get-analysis` | `{session_id}` | Detailed AI career analysis |
| POST | `/chat` | `{session_id, message}` | Chat with AI about the resume |
| POST | `/add-linkedin` | `{session_id, linkedin_url}` | Selenium-based LinkedIn scrape |
| POST | `/paste-linkedin` | `{session_id, linkedin_text}` | LLM extraction from pasted text *(preferred)* |
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
| GET | `/screening/job-requirements-template` | – | Sample requirements JSON |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + Redis + Groq dependency probes |
| GET | `/metrics` | Prometheus exposition (when `METRICS_ENABLED=true`) |
| GET | `/docs` | OpenAPI UI (dev only) |

---

## Workflows

### As a candidate

1. Drag a PDF resume onto the upload card (or click to browse). Inline progress; ~5–10 s.
2. Auto-redirect to `/analysis.html` with your extracted profile + AI analysis.
3. **Optionally** add a LinkedIn URL or paste profile text to enrich the data (paste is faster).
4. Click **Generate Job Recommendations** for matched roles.
5. Click the chat fab to ask the AI questions about your profile.
6. **Optionally** run **Check ATS** with a target job description for an ATS score.

The analysis page has a sticky table-of-contents rail on the left (desktop) to jump between sections.

### As a recruiter

1. Open `/screening.html`.
2. **Step 1** — define the role: title, required + preferred skills, experience range, degree.
3. **Step 2** — upload up to 50 candidate PDFs (drag-and-drop or click).
4. **Step 3** — review ranked candidates with skill match breakdowns and gaps.

Click **Load example spec** to populate the form with a sample for demos.

### Best practices

- Use **text-based PDFs** (selectable text, not scanned images)
- Include **complete work history** with dates and accomplishments
- For ATS checks, paste the **full job description**, not just the title
- For LinkedIn enrichment, prefer the **paste-text** flow over the URL scraper

---

## Frontend architecture

Vanilla HTML/CSS/JS with three layered stylesheets and a single interaction script:

- **`style.css`** — base layout, components, original token system
- **`motion.css`** — animations, transitions, toast styles, skeleton loaders, drag-and-drop visuals
- **`theme.css`** — current corporate/enterprise theme: flat surfaces, hairline borders, navy palette, Inter typography
- **`motion.js`** — exposes `window.UI.toast(msg, {type, duration})`, `UI.setLoading(btn, true)`, `UI.escape(str)`, `UI.html\`<p>${userInput}</p>\``. Auto-initializes scroll reveal, navbar elevation, ripple, count-up, mobile hamburger, drag-and-drop, sticky TOC, clipboard

All animation respects `prefers-reduced-motion`.

### Production asset optimization

When `ENV=production`, on app startup:

1. CSS files are minified with `csscompressor`
2. JS files are minified with `rjsmin`
3. Each minified file gets a 10-char SHA-256 hash appended to the filename (`theme.css → theme.3010d4674c.css`)
4. HTML responses are rewritten on the fly to reference the hashed names
5. Hashed assets ship with `Cache-Control: public, max-age=31536000, immutable`

Net effect: **~25% smaller payload + immutable browser caching** on every visit. Users never see stale CSS because the URL changes whenever the content does.

In development none of this runs — assets serve unmodified for fast iteration.

---

## Observability

### Logging

Plain text in development; structured JSON when `LOG_JSON=true`. Useful fields: `incident_id`, `session`, `error`. Every 5xx response includes the incident id in `detail` so server logs can be correlated to the user-facing message.

### Error tracking (optional, Sentry)

Set `SENTRY_DSN` and traces/profiles will flow into Sentry. `send_default_pii=False` so resume contents don't leak. Sample rates are env-configurable.

### Metrics (optional, Prometheus)

Set `METRICS_ENABLED=true` to register `/metrics` with the standard FastAPI request count and latency histogram. Optionally guard it with basic auth via `METRICS_BASIC_AUTH=user:pass`.

What you get:

- `http_requests_total{handler, status}` — request counts
- `http_request_duration_seconds` — latency histogram per route
- `python_gc_*`, `process_resident_memory_bytes`, etc.

### Health check

`GET /health` returns:

```json
{
  "status": "healthy",
  "service": "Resume Summarizer",
  "version": "1.1.0",
  "checks": {
    "redis": { "status": "ok" },
    "groq":  { "status": "ok" }
  }
}
```

Use this as a readiness probe. Results are cached for 5 seconds so probe spam doesn't hammer dependencies.

---

## Security

- API keys live in `.env` only (excluded from Docker via `.dockerignore`)
- File uploads validated by extension + 10 MB cap (`MAX_FILE_SIZE`)
- Session ids strictly validated: `^[A-Za-z0-9_-]{8,128}$`
- Per-IP rate limiting on every endpoint
- HTTP error responses don't leak `str(exception)` — incidents are logged with a UUID and the client gets a generic message + that UUID
- `/docs` hidden in production (`ENV=production`)
- XSS-safe rendering — all user/LLM-sourced text is escaped via `UI.escape` before DOM insertion; chatbot replies are rendered with `textContent`
- Static assets served with long-cache `immutable` only when the URL is content-hashed (production)

### Known caveats

- **Sessions are client-id-supplied.** The frontend generates a session id and passes it on every request. For higher-security deployments, switch to server-issued, httpOnly-cookie sessions before exposing this publicly.
- **No authentication.** Anyone with the URL can use it. Add an auth layer (or a reverse-proxy auth filter) before public exposure.
- **Selenium LinkedIn scraping** is fragile and ToS-iffy. The paste-text flow is the recommended path.

---

## Troubleshooting

**`GROQ_API_KEY not found in .env file`**
Make sure `.env` exists in the project root and contains a valid key.

**Port 8000 already in use**
Kill the existing process or run on another port: `uvicorn main:app --port 8001`.

**`Failed to extract text from PDF`**
The file is a scanned image. Use a text-based PDF or run OCR first.

**Session expired / "No resume uploaded for this session"**
Sessions live 1 hour by default (`SESSION_TIMEOUT`). Re-upload, or increase the value.

**LinkedIn scrape fails**
Selenium needs Chrome + a matching chromedriver. The app falls back to "resume-only" automatically — no hard failure. Use the **paste-text** flow instead if scraping keeps failing.

**Multi-worker session loss in production**
You're hitting different workers between requests. Set `SESSION_BACKEND=redis`.

**Stale CSS / JS after deploy**
In production this shouldn't happen — the asset URL changes whenever the file content changes. If it does happen, force-bump by setting `ENV=production` and restarting (manifest is rebuilt on app start).

---

## Development

### Run tests

```bash
pytest tests/
```

The suite has 24 tests; 2 are skipped by default (live Selenium + live Groq) unless `RUN_SELENIUM_TESTS=1` and a real `GROQ_API_KEY` are set.

### Style + pre-commit

```bash
pip install pre-commit
pre-commit install   # runs ruff + black + EOL/whitespace on every commit
```

Manual run:

```bash
ruff check .
ruff format .
black .
```

### Adding an endpoint

1. Add request schema to `app/models.py`
2. Add a method to the right handler class in `app/handlers.py` (or a new one)
3. Wire it in `main.py` with `@limiter.limit(...)` and an OpenAPI tag
4. Add at least one test to `tests/test_handlers.py`
5. Update this README's API table

See [CONTRIBUTING.md](CONTRIBUTING.md) for the longer guide.

---

## Contributing

1. Fork
2. `git checkout -b feature/your-thing`
3. Add tests
4. `pytest tests/` + `pre-commit run --all-files`
5. Open a PR (templates are in `.github/`)

CI runs pytest + Docker build on every PR.

---

## Changelog

### 1.2.0 (current)

**Frontend**
- **Corporate/enterprise theme** — flat surfaces, hairline borders, navy palette, Inter typography. Dropped glass blur, mesh gradients, conic halos.
- **Sticky table-of-contents rail** on the analysis page (desktop), with active-section tracking via IntersectionObserver
- **Per-page hero differentiation** — eyebrow labels + compact hero variant for tool pages
- **Paste-LinkedIn UI** with tabbed input (paste vs. URL) — paste is the preferred path
- **Mobile navigation** — hamburger toggle injected via JS, glass drawer below 720px
- **Real empty states** with iconography + actionable copy
- **Self-host hook for Inter** via `@font-face` with `local()` fallback; removed Google Fonts CDN dependency
- **XSS sanitization pass** across analysis, jobs, screening, and chatbot renderers (`UI.escape` helper)
- **Toast system** replaces every `alert()` call
- **Inline upload progress** replaces full-screen overlay
- **Drag-and-drop** on upload card with live state machine

**Backend / production hardening**
- **Static asset minify + content-hash + immutable caching** (production-only, pure-Python via `csscompressor` + `rjsmin`)
- **Prometheus `/metrics`** (opt-in, optional basic-auth)
- **`/health` probes Redis + Groq** with 5-second cache
- **paste-LinkedIn endpoint** (`/paste-linkedin`) — LLM extraction from pasted text, no Selenium required
- **`docker-compose.yml`** with app + Redis health check
- **Pre-commit + GitHub Actions CI** — ruff, black, pytest on push/PR
- **Pluggable `SessionManager`** with in-memory + Redis backends, thread-safe, background cleanup
- **`errors.py`** — incident-id'd safe HTTP errors (no `str(e)` leakage)
- **Rate limiting** via `slowapi` on every endpoint, per-route caps
- **Singleton `JobRecommender` and `ATSChecker`** in app `lifespan`
- **`FileResponse` for HTML routes** with proper caching headers
- **Strict `session_id` validation** (regex, 8–128 chars)
- **Replaced hardcoded fake market/job analysis stubs** with real LLM calls
- **Switched `PyPDF2` → `pypdf`**
- **Sentry integration** (env-gated on `SENTRY_DSN`)

### 1.0.0

- Initial release
- Resume upload and analysis
- AI-powered career insights
- Job recommendations
- LinkedIn integration
- Interactive chat assistant

---

Built with FastAPI + Groq. Frontend in vanilla HTML/CSS/JS. License: provided as-is for educational and professional use.
