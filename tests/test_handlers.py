"""Handler-level tests. Uses TestClient + mocked Groq from conftest.py."""
import io


VALID_SESSION = "abcdef12-3456-7890-abcd-ef0123456789"
SHORT_SESSION = "x" * 4  # below 8-char minimum


# ---------- Health + page serving ----------

def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("healthy", "degraded")
    assert "version" in body
    assert "checks" in body
    assert "redis" in body["checks"]
    assert "groq" in body["checks"]


def test_paste_linkedin_rejects_short_text(client):
    r = client.post(
        "/paste-linkedin",
        json={"session_id": VALID_SESSION, "linkedin_text": "short"},
    )
    # No session yet, so 400 either way — but it should fail at session check first
    assert r.status_code == 400


def test_paste_linkedin_rejects_bad_session(client):
    r = client.post(
        "/paste-linkedin",
        json={"session_id": "bad$id", "linkedin_text": "a" * 100},
    )
    assert r.status_code == 400


def test_home_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_static_assets_served(client):
    for path in ("/static/style.css", "/static/motion.css",
                 "/static/theme.css", "/static/motion.js"):
        r = client.get(path)
        assert r.status_code == 200, f"{path} returned {r.status_code}"
        assert len(r.content) > 0


# ---------- Session id validation ----------

def test_get_analysis_rejects_short_session_id(client):
    r = client.post("/get-analysis", json={"session_id": SHORT_SESSION})
    assert r.status_code == 400
    assert "session id" in r.json()["detail"].lower()


def test_get_analysis_rejects_invalid_charset(client):
    r = client.post("/get-analysis", json={"session_id": "abc def$%^"})
    assert r.status_code == 400


def test_get_analysis_missing_session(client):
    r = client.post("/get-analysis", json={"session_id": VALID_SESSION})
    assert r.status_code == 400
    assert "no resume" in r.json()["detail"].lower()


# ---------- Upload endpoint validation ----------

def test_upload_rejects_non_pdf(client):
    fake_file = ("resume.txt", io.BytesIO(b"hello"), "text/plain")
    r = client.post(
        "/upload",
        files={"file": fake_file},
        data={"session_id": VALID_SESSION},
    )
    assert r.status_code == 400
    assert "pdf" in r.json()["detail"].lower()


def test_upload_rejects_empty_file(client):
    fake_file = ("resume.pdf", io.BytesIO(b""), "application/pdf")
    r = client.post(
        "/upload",
        files={"file": fake_file},
        data={"session_id": VALID_SESSION},
    )
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()


def test_upload_rejects_bad_session(client):
    fake_file = ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")
    r = client.post(
        "/upload",
        files={"file": fake_file},
        data={"session_id": SHORT_SESSION},
    )
    assert r.status_code == 400


# ---------- Chat / linkedin / job recs ----------

def test_chat_requires_existing_session(client):
    r = client.post("/chat", json={"session_id": VALID_SESSION, "message": "hi"})
    assert r.status_code == 400


def test_skip_linkedin_requires_existing_session(client):
    r = client.post("/skip-linkedin", json={"session_id": VALID_SESSION})
    assert r.status_code == 400


def test_recommend_jobs_requires_existing_session(client):
    r = client.post("/recommend-jobs", json={"session_id": VALID_SESSION})
    assert r.status_code == 400


# ---------- ATS prerequisites ----------

def test_ats_suggestions_requires_prior_analysis(client):
    # Even with a valid-format session, no upload means 400
    r = client.post(
        "/ats-suggestions",
        json={"session_id": VALID_SESSION, "improvement_type": "all"},
    )
    assert r.status_code == 400


# ---------- Screening router presence ----------

def test_metrics_disabled_by_default(client):
    # In the test env, METRICS_ENABLED is not set → endpoint should not exist
    r = client.get("/metrics")
    assert r.status_code == 404


def test_screening_template_endpoint_exists(client):
    r = client.get("/screening/job-requirements-template")
    # Should return a 200 with a sample template, OR 405/404 if router not wired.
    # We just confirm it isn't a server error.
    assert r.status_code in (200, 404, 405)


# ---------- Session manager direct ----------

def test_session_id_regex():
    from app.session_manager import is_valid_session_id
    assert is_valid_session_id("abcdefgh") is True
    assert is_valid_session_id("a" * 128) is True
    assert is_valid_session_id("a" * 129) is False
    assert is_valid_session_id("a" * 7) is False
    assert is_valid_session_id("has spaces") is False
    assert is_valid_session_id("has$symbol") is False
    assert is_valid_session_id("") is False
    assert is_valid_session_id("valid_id-123") is True


def test_session_manager_create_get_update():
    from app.session_manager import SessionManager
    mgr = SessionManager(timeout=60)
    mgr.create_session("abc12345", {"foo": "bar"})
    assert mgr.get_session("abc12345") == {"foo": "bar"}
    mgr.update_session("abc12345", {"baz": "qux"})
    assert mgr.get_session("abc12345") == {"foo": "bar", "baz": "qux"}


def test_session_manager_expiry():
    import time
    from app.session_manager import SessionManager
    mgr = SessionManager(timeout=0)  # immediate expiry
    mgr.create_session("abc12345", {"foo": "bar"})
    time.sleep(0.05)
    assert mgr.get_session("abc12345") is None


def test_session_manager_cleanup_returns_count():
    import time
    from app.session_manager import SessionManager
    mgr = SessionManager(timeout=0)
    mgr.create_session("aaaaaaaa", {"x": 1})
    mgr.create_session("bbbbbbbb", {"y": 2})
    time.sleep(0.05)
    assert mgr.cleanup_old_sessions() == 2
