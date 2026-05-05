let sessionId = Date.now().toString() + Math.random().toString(36).slice(2, 10);

document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("resumeFile");
    if (!fileInput) {
        console.error("Resume file input not found!");
        return;
    }
    fileInput.addEventListener("change", handleFileSelected);
});

async function handleFileSelected(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;

    const fileNameEl = document.getElementById("fileName");
    const progressEl = document.getElementById("uploadProgress");
    const statusEl = document.getElementById("uploadStatus");
    const legacyStatusEl = document.getElementById("status");
    const overlayEl = document.getElementById("loading");
    const chooseBtn = document.querySelector(".upload-actions .btn-primary");

    if (fileNameEl) fileNameEl.textContent = file.name;
    if (legacyStatusEl) legacyStatusEl.style.display = "none";
    if (overlayEl) overlayEl.style.display = "none"; // suppress old overlay
    if (progressEl) progressEl.classList.add("is-active");
    if (statusEl) {
        statusEl.classList.remove("is-success", "is-error");
        statusEl.textContent = "Uploading and analyzing…";
    }
    if (window.UI) UI.setLoading(chooseBtn, true);

    const fd = new FormData();
    fd.append("file", file);
    fd.append("session_id", sessionId);

    try {
        const res = await fetch("/upload", { method: "POST", body: fd });
        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            const detail = data.detail || `Upload failed (${res.status})`;
            handleUploadFailure(detail, statusEl, progressEl, chooseBtn);
            return;
        }

        if (statusEl) {
            statusEl.classList.add("is-success");
            statusEl.textContent = "✓ Analyzed. Redirecting to your results…";
        }
        if (window.UI) UI.toast("Resume analyzed successfully", { type: "success" });

        localStorage.setItem("sessionId", sessionId);
        const redirectUrl = `/analysis.html?session=${encodeURIComponent(sessionId)}`;
        setTimeout(() => { window.location.href = redirectUrl; }, 900);
    } catch (err) {
        console.error("Upload error:", err);
        handleUploadFailure(
            "Network error. Check your connection and try again.",
            statusEl, progressEl, chooseBtn
        );
    } finally {
        if (window.UI) UI.setLoading(chooseBtn, false);
    }
}

function handleUploadFailure(message, statusEl, progressEl, chooseBtn) {
    if (progressEl) progressEl.classList.remove("is-active");
    if (statusEl) {
        statusEl.classList.add("is-error");
        statusEl.textContent = message;
    }
    if (window.UI) {
        UI.toast(message, { type: "error", duration: 5000 });
        UI.setLoading(chooseBtn, false);
    }
}
