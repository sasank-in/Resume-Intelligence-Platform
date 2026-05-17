"""Static asset minification + content-hash cache busting.

On app startup (production only) we walk the static dir, minify CSS/JS, and
write the result to an in-memory map keyed by *hashed filename*. We also
emit a manifest of ``original -> hashed`` so we can rewrite HTML references
on the fly.

In development we serve files unmodified through the regular StaticFiles
mount and skip rewriting entirely. The minify libraries are optional —
if they aren't installed we fall back to passthrough.

Why this exists: long-cache headers on /static/* are unsafe unless the URL
changes whenever the content changes. Hashing the filename lets us return
``Cache-Control: public, max-age=31536000, immutable`` safely.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .logging_config import get_logger

log = get_logger(__name__)

# Try optional minify deps. If absent, we just hash + serve raw.
try:
    import csscompressor  # type: ignore
except ImportError:  # pragma: no cover
    csscompressor = None
try:
    import rjsmin  # type: ignore
except ImportError:  # pragma: no cover
    rjsmin = None

_HASH_LEN = 10


@dataclass(frozen=True)
class Asset:
    original_name: str   # e.g. "theme.css"
    hashed_name: str     # e.g. "theme.abc1234567.css"
    content: bytes       # bytes ready to ship (minified if applicable)
    content_type: str    # text/css | application/javascript | etc.


class StaticManifest:
    """Owns the minified, hashed copies of static assets in memory."""

    # Asset types we minify + hash. Everything else stays under raw StaticFiles.
    MINIFY_EXTENSIONS = {
        ".css": ("text/css; charset=utf-8", "css"),
        ".js":  ("application/javascript; charset=utf-8", "js"),
    }

    def __init__(self, static_dir: Path):
        self.static_dir = static_dir
        # hashed_name -> Asset
        self.assets: Dict[str, Asset] = {}
        # original_name -> hashed_name (used by HTML rewriter)
        self.manifest: Dict[str, str] = {}

    def build(self) -> None:
        if not self.static_dir.is_dir():
            log.warning("static_dir_missing", extra={"path": str(self.static_dir)})
            return

        for path in self.static_dir.iterdir():
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            if ext not in self.MINIFY_EXTENSIONS:
                continue
            content_type, kind = self.MINIFY_EXTENSIONS[ext]
            raw = path.read_bytes()
            minified = self._minify(raw, kind)
            digest = hashlib.sha256(minified).hexdigest()[:_HASH_LEN]
            hashed_name = f"{path.stem}.{digest}{ext}"
            asset = Asset(
                original_name=path.name,
                hashed_name=hashed_name,
                content=minified,
                content_type=content_type,
            )
            self.assets[hashed_name] = asset
            self.manifest[path.name] = hashed_name

        log.info(
            "static_manifest_built",
            extra={
                "count": len(self.assets),
                "savings_bytes": self._total_savings(),
            },
        )

    @staticmethod
    def _minify(raw: bytes, kind: str) -> bytes:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw
        if kind == "css" and csscompressor is not None:
            try:
                return csscompressor.compress(text).encode("utf-8")
            except Exception:  # noqa: BLE001
                log.exception("css_minify_failed")
                return raw
        if kind == "js" and rjsmin is not None:
            try:
                return rjsmin.jsmin(text).encode("utf-8")
            except Exception:  # noqa: BLE001
                log.exception("js_minify_failed")
                return raw
        return raw

    def _total_savings(self) -> int:
        total = 0
        for hashed, asset in self.assets.items():
            try:
                original_size = (self.static_dir / asset.original_name).stat().st_size
                total += original_size - len(asset.content)
            except OSError:
                continue
        return total


# ---------- HTML rewriter ----------

# Match href="/static/<name>" or src="/static/<name>" (optionally with quotes,
# slashes vary, no fragments expected on these refs). Conservative regex:
# only rewrite assets we have a hashed version for. Anything not in the
# manifest is left alone.
_STATIC_REF = re.compile(
    r'(?P<attr>href|src)="/static/(?P<name>[A-Za-z0-9._-]+)"'
)


def rewrite_html(html_text: str, manifest: Dict[str, str]) -> str:
    """Rewrite /static/foo.css → /static/foo.abc123.css for known assets."""
    if not manifest:
        return html_text

    def sub(match: re.Match) -> str:
        name = match.group("name")
        hashed = manifest.get(name)
        if not hashed:
            return match.group(0)
        return f'{match.group("attr")}="/static/{hashed}"'

    return _STATIC_REF.sub(sub, html_text)


# ---------- FastAPI helpers ----------

def make_static_handler(manifest: StaticManifest):
    """Returns an async route handler for /static/<hashed-name>."""
    from fastapi import HTTPException
    from fastapi.responses import Response

    LONG_CACHE = "public, max-age=31536000, immutable"

    async def serve(filename: str) -> Response:
        asset = manifest.assets.get(filename)
        if asset is None:
            raise HTTPException(status_code=404, detail="asset not found")
        return Response(
            content=asset.content,
            media_type=asset.content_type,
            headers={"Cache-Control": LONG_CACHE},
        )

    return serve


def serve_html_with_rewrite(path: Path, manifest: Optional[StaticManifest]):
    """Return the HTML body with static refs rewritten to hashed versions."""
    from fastapi import HTTPException
    from fastapi.responses import HTMLResponse

    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if manifest is not None:
        text = rewrite_html(text, manifest.manifest)
    # HTML itself should NOT be aggressively cached; the hashed asset refs do the work.
    return HTMLResponse(
        text,
        headers={"Cache-Control": "no-cache, must-revalidate"},
    )
