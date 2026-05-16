# Contributing

Thanks for your interest in improving Resume Analyzer Pro. This guide gets you set
up in under five minutes.

## Setup

```bash
git clone <repo>
cd resume-summarizer
pip install -r requirements.txt
pip install pre-commit && pre-commit install
cp .env.example .env   # add your GROQ_API_KEY
python main.py
```

Open http://localhost:8000. Tests:

```bash
pytest tests/
```

## Project layout

- `app/` — FastAPI layer: routes, handlers, services, session manager, logging, errors
- `src/` — domain modules: parsers, scrapers, recommenders, builders
- `static/` — vanilla HTML/CSS/JS frontend (three CSS layers: `style.css` base, `motion.css` interactions, `theme.css` visual theme)
- `tests/` — pytest. `conftest.py` provides a `client` fixture with mocked Groq

## What goes where

| You want to… | Edit |
|---|---|
| Add an endpoint | `app/handlers.py` + wire it in `main.py` with a `@limiter.limit(...)` |
| Add a request schema | `app/models.py` |
| Change an LLM prompt | `app/services.py` |
| Touch session storage | `app/session_manager.py` |
| Add resume parsing logic | `src/parsers/resume_parser.py` |
| Change UI animation | `static/motion.css` + `motion.js` |
| Change UI theme/colors | `static/theme.css` only — leave `style.css` alone |

## Style

- Code: `black .` + `ruff check .` (both run by pre-commit)
- Imports: ruff handles ordering
- Logging: use `from app.logging_config import get_logger` — never raw `print()` in `app/`. In `src/` the `print` symbol is auto-routed to `logging` via `src/_logprint.py`, so existing prints there are fine
- Error responses: use `app/errors.py` helpers (`bad_request`, `server_error`) — never put `str(exception)` in `HTTPException.detail`
- Comments: only when WHY is non-obvious. Don't restate WHAT the code does

## Tests

- Handler tests live in `tests/test_handlers.py` and use the `client` fixture (mocked Groq)
- The system smoke test in `tests/test_system.py` skips Selenium and live-Groq calls unless explicitly enabled via env vars
- When adding a route, add at least one test for: 200 happy path, 400 on bad input, 400 when prerequisites aren't met
- Aim for tests that run in <2s without network. If you need to test the real Groq API, gate it on an env flag like `test_groq_api_live` does

## Adding an endpoint — recipe

1. Schema in `app/models.py`
2. Handler method in the appropriate class in `app/handlers.py` (or new class)
3. Route in `main.py` with `@limiter.limit(...)`
4. Tests in `tests/test_handlers.py`
5. README API table entry

## Frontend changes

- Reload may be cached aggressively. Always test with hard refresh (Ctrl+F5)
- `motion.js` exposes `window.UI.toast()`, `UI.setLoading(btn, true)`, `UI.skeleton.*` — prefer these to inline `alert()` or ad-hoc spinners
- All animation must respect `prefers-reduced-motion` (the existing CSS already gates everything; just don't add unconditional JS animations)
- Every new HTML page should include the three CSS files in order: `style.css`, `motion.css`, `theme.css`

## Commit & PR

- One topic per PR — keep the diff readable
- Reference the issue you're closing (`Fixes #42`)
- Description: what changed, why, how to verify
- CI must be green (`pytest` + Docker build)
- A reviewer will look at it within a few days

## Questions

Open a draft PR with a `[WIP]` prefix and tag it with `question`, or open a discussion if your idea is bigger than one PR.
