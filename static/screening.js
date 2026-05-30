// Resume Screening System JavaScript

let selectedFiles = [];

function formatBytes(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function renderFileList() {
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    const fileList = document.getElementById('fileList');
    const screenBtn = document.getElementById('screenBtn');

    if (selectedFiles.length === 0) {
        fileList.style.display = 'none';
        fileList.innerHTML = '';
        screenBtn.disabled = true;
        return;
    }

    fileList.style.display = 'flex';
    fileList.className = 'file-list';
    fileList.innerHTML = selectedFiles.map((f, i) => `
        <div class="file-item">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--gray-500); flex-shrink: 0;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
            </svg>
            <span class="file-item-name" title="${esc(f.name)}">${esc(f.name)}</span>
            <span class="file-item-size">${formatBytes(f.size)}</span>
            <button type="button" class="file-item-remove" data-index="${i}" aria-label="Remove ${esc(f.name)}">×</button>
        </div>
    `).join('');
    screenBtn.disabled = false;
}

function addFiles(incoming) {
    const accepted = [];
    const rejected = [];
    for (const f of incoming) {
        if (f.name.toLowerCase().endsWith('.pdf')) accepted.push(f);
        else rejected.push(f.name);
    }
    if (rejected.length && window.UI) {
        UI.toast(`Skipped ${rejected.length} non-PDF file(s)`, { type: 'info' });
    }
    // De-dupe by name+size
    const seen = new Set(selectedFiles.map(f => `${f.name}:${f.size}`));
    for (const f of accepted) {
        const key = `${f.name}:${f.size}`;
        if (!seen.has(key)) { selectedFiles.push(f); seen.add(key); }
    }
    renderFileList();
}

function removeFileAt(index) {
    if (index >= 0 && index < selectedFiles.length) {
        selectedFiles.splice(index, 1);
        renderFileList();
    }
}

function handleFileSelection() {
    const fileInput = document.getElementById('resumeFiles');
    addFiles(Array.from(fileInput.files));
    // Reset native input so re-picking the same file fires `change`
    fileInput.value = '';
}

// Delegated click handler for per-file remove buttons
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.file-item-remove');
    if (btn) {
        const idx = parseInt(btn.getAttribute('data-index'), 10);
        if (!isNaN(idx)) removeFileAt(idx);
    }
});

function getJobRequirements() {
    const requiredSkills = document.getElementById('requiredSkills').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    
    const preferredSkills = document.getElementById('preferredSkills').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    
    return {
        job_title: document.getElementById('jobTitle').value,
        required_skills: requiredSkills,
        preferred_skills: preferredSkills,
        min_experience_years: parseFloat(document.getElementById('minExperience').value) || 0,
        max_experience_years: parseFloat(document.getElementById('maxExperience').value) || 100,
        required_degree: document.getElementById('requiredDegree').value || null
    };
}

async function screenResumes() {
    if (selectedFiles.length === 0) {
        if (window.UI) UI.toast('Please select at least one resume PDF', { type: 'info' });
        return;
    }

    const jobRequirements = getJobRequirements();

    if (!jobRequirements.job_title) {
        if (window.UI) UI.toast('Please enter a job title', { type: 'info' });
        return;
    }

    if (jobRequirements.required_skills.length === 0) {
        if (window.UI) UI.toast('Please enter at least one required skill', { type: 'info' });
        return;
    }

    const loadingOverlay = document.getElementById('loadingOverlay');
    const progressText = document.getElementById('progressText');
    loadingOverlay.style.display = 'flex';

    const total = selectedFiles.length;
    // Backend is a single batch request — we don't get streamed progress.
    // Estimate ~1.2s per resume and animate the counter so the user sees movement.
    let current = 0;
    progressText.textContent = `Processing 0 of ${total} resume(s)…`;
    const tick = setInterval(() => {
        if (current < total - 1) {
            current += 1;
            progressText.textContent = `Processing ${current} of ${total} resume(s)…`;
        }
    }, Math.max(800, 1200));

    try {
        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        formData.append('job_requirements', JSON.stringify(jobRequirements));

        const fetchPromise = fetch('/screening/screen-batch', {
            method: 'POST',
            body: formData
        });
        const response = await (window.UI ? UI.withSlowToast(fetchPromise,
            `Still screening ${total} resume(s) — this can take 30–90 s for large batches.`,
            { delay: 6000 }
        ) : fetchPromise);

        const data = await response.json();

        if (response.ok && data.success) {
            progressText.textContent = `Processed ${total} of ${total} resume(s) ✓`;
            displayResults(data);
            if (window.UI) UI.toast(`Screened ${total} candidates`, { type: 'success' });
        } else {
            throw new Error(data.detail || 'Screening failed');
        }
    } catch (error) {
        console.error('Screening error:', error);
        if (window.UI) UI.toast('Screening failed — ' + error.message, { type: 'error', duration: 6000 });
    } finally {
        clearInterval(tick);
        // small delay so the user briefly sees the "done" state
        setTimeout(() => { loadingOverlay.style.display = 'none'; }, 350);
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const summaryStats = document.getElementById('summaryStats');
    const topCandidates = document.getElementById('topCandidates');
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));

    resultsSection.style.display = 'block';

    const summary = data.summary || {};
    summaryStats.innerHTML = `
        <div class="stat-item"><div class="stat-value">${esc(summary.total_processed ?? '—')}</div><div class="stat-label">Total Processed</div></div>
        <div class="stat-item highlight"><div class="stat-value">${esc(summary.highly_recommended ?? '—')}</div><div class="stat-label">Highly Recommended</div></div>
        <div class="stat-item"><div class="stat-value">${esc(summary.recommended ?? '—')}</div><div class="stat-label">Recommended</div></div>
        <div class="stat-item"><div class="stat-value">${esc(summary.maybe ?? '—')}</div><div class="stat-label">Maybe</div></div>
        <div class="stat-item"><div class="stat-value">${typeof summary.average_score === 'number' ? summary.average_score.toFixed(1) : '—'}</div><div class="stat-label">Average Score</div></div>
    `;

    if (data.top_candidates && data.top_candidates.length > 0) {
        topCandidates.innerHTML = `
            <h3 class="results-heading">Top Candidates</h3>
            <div class="job-recommendations-grid">
                ${data.top_candidates.map(c => createCandidateCard(c)).join('')}
            </div>
        `;
    } else {
        topCandidates.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <line x1="22" y1="8" x2="17" y2="13"/>
                        <line x1="17" y1="8" x2="22" y2="13"/>
                    </svg>
                </div>
                <h3>No candidates matched the criteria</h3>
                <p>Try loosening your required skills, experience range, or required degree.</p>
            </div>`;
    }

    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function createCandidateCard(candidate) {
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    const statusColors = {
        'HIGHLY_RECOMMENDED': '#10b981',
        'RECOMMENDED': '#6366f1',
        'MAYBE': '#f59e0b',
        'NOT_RECOMMENDED': '#ef4444'
    };
    const statusColor = statusColors[candidate.status] || '#6b7280';
    const strengths = Array.isArray(candidate.key_strengths) ? candidate.key_strengths : [];
    const statusLabel = (candidate.status || '').replace(/_/g, ' ');

    return `
        <div class="job-card">
            <div class="job-header">
                <div>
                    <h3 class="candidate-name">Rank #${esc(candidate.rank)}: ${esc(candidate.name || 'N/A')}</h3>
                    <p class="candidate-contact">
                        ${esc(candidate.email || 'No email')} · ${esc(candidate.phone || 'No phone')}
                    </p>
                </div>
                <div class="match-score" style="background: ${statusColor};">
                    ${esc(candidate.score)}/100
                </div>
            </div>

            <div class="candidate-status-row">
                <span class="status-pill" style="background: ${statusColor}1f; color: ${statusColor};">
                    ${esc(statusLabel)}
                </span>
            </div>

            ${strengths.length > 0 ? `
                <div class="job-section">
                    <h4>Key Strengths</h4>
                    <div class="skills-tags">
                        ${strengths.map(s => `<span class="skill-tag match">${esc(s)}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

function loadTemplate() {
    // Warn before clobbering non-empty fields
    const fields = ['jobTitle', 'requiredSkills', 'preferredSkills'];
    const hasData = fields.some(id => (document.getElementById(id).value || '').trim().length > 0);
    if (hasData && !confirm('This will overwrite your current job requirements. Continue?')) {
        return;
    }

    fetch('/screening/job-requirements-template')
        .then(response => response.json())
        .then(template => {
            document.getElementById('jobTitle').value = template.job_title;
            document.getElementById('requiredSkills').value = template.required_skills.join(', ');
            document.getElementById('preferredSkills').value = template.preferred_skills.join(', ');
            document.getElementById('minExperience').value = template.min_experience_years;
            document.getElementById('maxExperience').value = template.max_experience_years;
            document.getElementById('requiredDegree').value = template.required_degree || '';

            if (window.UI) UI.toast('Template loaded', { type: 'success' });
        })
        .catch(error => {
            console.error('Error loading template:', error);
            if (window.UI) UI.toast('Failed to load template', { type: 'error' });
        });
}

// Whole-page drop overlay — drag a PDF anywhere on the screening page
(function initDropOverlay() {
    let dragCounter = 0;
    let overlay = document.getElementById('screeningDropzone');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'screeningDropzone';
        overlay.className = 'dropzone-overlay';
        overlay.innerHTML = `
            <div style="text-align: center;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="display: block; margin: 0 auto 0.75rem;">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 3 7 8"/>
                    <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                Drop PDF resumes anywhere to upload
            </div>
        `;
        document.body.appendChild(overlay);
    }
    const isFileDrag = (e) => Array.from(e.dataTransfer?.types || []).includes('Files');

    window.addEventListener('dragenter', (e) => {
        if (!isFileDrag(e)) return;
        dragCounter++;
        overlay.classList.add('is-active');
    });
    window.addEventListener('dragover', (e) => {
        if (!isFileDrag(e)) return;
        e.preventDefault();
    });
    window.addEventListener('dragleave', () => {
        dragCounter = Math.max(0, dragCounter - 1);
        if (dragCounter === 0) overlay.classList.remove('is-active');
    });
    window.addEventListener('drop', (e) => {
        if (!isFileDrag(e)) return;
        e.preventDefault();
        dragCounter = 0;
        overlay.classList.remove('is-active');
        const files = Array.from(e.dataTransfer.files);
        if (files.length) addFiles(files);
    });
})();
