/* motion.js — interaction layer. Page-agnostic; safe to load on every page. */
(function () {
    "use strict";

    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- Scroll reveal ---------- */
    function initReveal() {
        const targets = document.querySelectorAll("[data-reveal]");
        if (!targets.length) return;
        if (reduce || !("IntersectionObserver" in window)) {
            targets.forEach(el => el.classList.add("is-visible"));
            return;
        }
        const io = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.classList.add("is-visible");
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
        targets.forEach(el => io.observe(el));
    }

    /* ---------- Navbar shadow on scroll + mobile hamburger ---------- */
    function initNavbar() {
        const nav = document.querySelector(".navbar");
        if (!nav) return;
        const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 8);
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });

        // active link highlight
        const path = window.location.pathname;
        nav.querySelectorAll(".nav-link").forEach(a => {
            const href = a.getAttribute("href");
            if (!href) return;
            if (
                (href === "/" && (path === "/" || path === "/index.html")) ||
                (href !== "/" && path.endsWith(href))
            ) {
                a.classList.add("is-active");
            }
        });

        // Inject hamburger toggle (CSS shows it only below 720px)
        const container = nav.querySelector(".nav-container");
        const links = nav.querySelector(".nav-links");
        if (!container || !links || container.querySelector(".nav-toggle")) return;

        const btn = document.createElement("button");
        btn.className = "nav-toggle";
        btn.setAttribute("aria-label", "Open navigation menu");
        btn.setAttribute("aria-expanded", "false");
        btn.setAttribute("aria-controls", "primaryNav");
        btn.innerHTML = '<span></span><span></span><span></span>';
        container.appendChild(btn);
        links.id = "primaryNav";

        const close = () => {
            nav.classList.remove("is-open");
            btn.setAttribute("aria-expanded", "false");
            btn.setAttribute("aria-label", "Open navigation menu");
        };
        const open = () => {
            nav.classList.add("is-open");
            btn.setAttribute("aria-expanded", "true");
            btn.setAttribute("aria-label", "Close navigation menu");
        };

        btn.addEventListener("click", () => {
            if (nav.classList.contains("is-open")) close();
            else open();
        });
        // Close on link click or escape or resize-to-desktop
        links.addEventListener("click", (e) => {
            if (e.target.closest(".nav-link")) close();
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && nav.classList.contains("is-open")) close();
        });
        window.addEventListener("resize", () => {
            if (window.innerWidth > 720 && nav.classList.contains("is-open")) close();
        });
    }

    /* ---------- Button ripple + auto loading state ---------- */
    function initButtons() {
        document.addEventListener("click", (e) => {
            const btn = e.target.closest(".btn");
            if (!btn || reduce) return;
            const rect = btn.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const ripple = document.createElement("span");
            ripple.className = "ripple";
            ripple.style.width = ripple.style.height = size + "px";
            ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
            ripple.style.top  = (e.clientY - rect.top  - size / 2) + "px";
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 650);
        });
    }

    /* ---------- Toasts ---------- */
    function ensureToastContainer() {
        let c = document.querySelector(".toast-container");
        if (!c) {
            c = document.createElement("div");
            c.className = "toast-container";
            c.setAttribute("role", "status");
            c.setAttribute("aria-live", "polite");
            document.body.appendChild(c);
        }
        return c;
    }

    function toast(message, opts) {
        const { type = "info", duration = 4000 } = opts || {};
        const container = ensureToastContainer();
        const el = document.createElement("div");
        el.className = `toast toast-${type}`;
        const icon = type === "success" ? "✓" : type === "error" ? "!" : "i";
        el.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-body"></div>
            <button class="toast-close" aria-label="Dismiss">×</button>`;
        el.querySelector(".toast-body").textContent = message;
        container.appendChild(el);
        requestAnimationFrame(() => el.classList.add("is-visible"));

        const dismiss = () => {
            el.classList.remove("is-visible");
            el.classList.add("is-leaving");
            setTimeout(() => el.remove(), 300);
        };
        el.querySelector(".toast-close").addEventListener("click", dismiss);
        if (duration > 0) setTimeout(dismiss, duration);
        return { dismiss };
    }

    /* ---------- Count-up for .stat-value with [data-count] ---------- */
    function initCounters() {
        const items = document.querySelectorAll(".stat-item");
        if (!items.length || reduce || !("IntersectionObserver" in window)) {
            items.forEach(i => i.classList.add("is-visible"));
            return;
        }
        const io = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (!e.isIntersecting) return;
                e.target.classList.add("is-visible");
                const valueEl = e.target.querySelector(".stat-value");
                const target = valueEl && valueEl.getAttribute("data-count");
                if (valueEl && target) {
                    countUp(valueEl, parseFloat(target),
                            valueEl.getAttribute("data-suffix") || "");
                }
                io.unobserve(e.target);
            });
        }, { threshold: 0.4 });
        items.forEach(i => io.observe(i));
    }

    function countUp(el, target, suffix) {
        const duration = 900;
        const start = performance.now();
        const isInt = Number.isInteger(target);
        function frame(now) {
            const t = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - t, 3);
            const value = target * eased;
            el.textContent = (isInt ? Math.round(value) : value.toFixed(1)) + suffix;
            if (t < 1) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    /* ---------- Copy to clipboard ---------- */
    function initClipboard() {
        document.addEventListener("click", async (e) => {
            const t = e.target.closest("[data-copy]");
            if (!t) return;
            const text = t.getAttribute("data-copy") || t.textContent.trim();
            try {
                await navigator.clipboard.writeText(text);
                t.classList.add("copied");
                setTimeout(() => t.classList.remove("copied"), 1300);
            } catch {
                toast("Could not copy to clipboard", { type: "error" });
            }
        });
    }

    /* ---------- Drag & drop for upload card ---------- */
    function initDropzone() {
        const card = document.querySelector(".upload-card");
        const input = document.getElementById("resumeFile");
        if (!card || !input) return;
        ["dragenter", "dragover"].forEach(ev =>
            card.addEventListener(ev, (e) => {
                e.preventDefault(); e.stopPropagation();
                card.classList.add("is-dragging");
            }));
        ["dragleave", "drop"].forEach(ev =>
            card.addEventListener(ev, (e) => {
                e.preventDefault(); e.stopPropagation();
                card.classList.remove("is-dragging");
            }));
        card.addEventListener("drop", (e) => {
            const files = e.dataTransfer && e.dataTransfer.files;
            if (!files || !files.length) return;
            // Assign to input and dispatch change so existing handler runs.
            const dt = new DataTransfer();
            dt.items.add(files[0]);
            input.files = dt.files;
            input.dispatchEvent(new Event("change", { bubbles: true }));
        });
    }

    /* ---------- Smooth-scroll same-page anchors ---------- */
    function initAnchors() {
        document.addEventListener("click", (e) => {
            const a = e.target.closest('a[href^="#"]');
            if (!a) return;
            const id = a.getAttribute("href").slice(1);
            if (!id) return;
            const target = document.getElementById(id);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
        });
    }

    /* ---------- HTML escape — defense against XSS via innerHTML ---------- */
    const _escMap = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
    function escape(str) {
        if (str == null) return "";
        return String(str).replace(/[&<>"']/g, ch => _escMap[ch]);
    }
    // Template tag: html`<p>${userInput}</p>` — auto-escapes interpolations.
    function html(strings, ...values) {
        let out = strings[0];
        for (let i = 0; i < values.length; i++) {
            out += escape(values[i]) + strings[i + 1];
        }
        return out;
    }

    /* ---------- Slow-call notifier ---------- */
    // Wraps an async operation: if it doesn't resolve within `delay` ms,
    // shows a persistent toast with the supplied message. Toast auto-dismisses
    // when the promise settles. Useful for LLM round-trips that often
    // take longer than users expect.
    function withSlowToast(promise, msg, opts) {
        const delay = (opts && opts.delay) || 5000;
        let handle = null;
        const timer = setTimeout(() => {
            handle = toast(msg || "Still working — this can take a few seconds…", {
                type: "info",
                duration: 0,  // sticky
            });
        }, delay);
        return promise.finally(() => {
            clearTimeout(timer);
            if (handle && handle.dismiss) handle.dismiss();
        });
    }

    /* ---------- Public API ---------- */
    window.UI = Object.freeze({
        toast,
        escape,
        html,
        withSlowToast,
        setLoading(btn, loading) {
            if (!btn) return;
            if (loading) btn.setAttribute("data-loading", "true");
            else btn.removeAttribute("data-loading");
        },
        skeleton: {
            line: (cls = "") => `<div class="skeleton skeleton-line ${cls}"></div>`,
            block: (cls = "") => `<div class="skeleton skeleton-block ${cls}"></div>`,
        },
    });

    /* ---------- Sticky TOC: highlight active section + hide rows for hidden sections ---------- */
    function initToc() {
        const links = Array.from(document.querySelectorAll(".toc-link"));
        if (!links.length) return;

        const linkByTarget = new Map(
            links.map(a => [a.getAttribute("data-target") || (a.getAttribute("href") || "").slice(1), a])
        );

        function refreshHiddenLinks() {
            for (const [id, link] of linkByTarget.entries()) {
                const section = document.getElementById(id);
                const hidden = !section || section.offsetParent === null;
                link.classList.toggle("is-hidden", hidden);
            }
        }
        refreshHiddenLinks();
        // The page's other JS toggles section visibility over time (linkedin, analysis,
        // job recommendations…). Poll briefly so the TOC stays accurate without coupling.
        let polls = 0;
        const poll = setInterval(() => {
            refreshHiddenLinks();
            if (++polls > 20) clearInterval(poll);  // ~10s total
        }, 500);

        if (!("IntersectionObserver" in window)) return;

        const io = new IntersectionObserver((entries) => {
            // Pick the entry that's most prominently in view
            const visible = entries
                .filter(e => e.isIntersecting)
                .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
            if (!visible.length) return;
            const id = visible[0].target.id;
            for (const link of links) link.classList.remove("is-active");
            const active = linkByTarget.get(id);
            if (active) active.classList.add("is-active");
        }, {
            rootMargin: "-30% 0px -55% 0px",
            threshold: [0, 0.25, 0.5, 0.75, 1],
        });

        for (const id of linkByTarget.keys()) {
            const section = document.getElementById(id);
            if (section) io.observe(section);
        }
    }

    /* ---------- Bootstrap ---------- */
    document.addEventListener("DOMContentLoaded", () => {
        initReveal();
        initNavbar();
        initButtons();
        initCounters();
        initClipboard();
        initDropzone();
        initAnchors();
        initToc();
    });
})();
