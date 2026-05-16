// Resume Screening System JavaScript

let selectedFiles = [];

function handleFileSelection() {
    const fileInput = document.getElementById('resumeFiles');
    selectedFiles = Array.from(fileInput.files);
    
    const fileList = document.getElementById('fileList');
    const screenBtn = document.getElementById('screenBtn');
    
    if (selectedFiles.length > 0) {
        fileList.style.display = 'block';
        fileList.innerHTML = `
            <strong>${selectedFiles.length} file(s) selected:</strong><br>
            ${selectedFiles.map(f => f.name).join('<br>')}
        `;
        screenBtn.disabled = false;
    } else {
        fileList.style.display = 'none';
        screenBtn.disabled = true;
    }
}

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

        const response = await fetch('/screening/screen-batch', {
            method: 'POST',
            body: formData
        });

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

// Drag and drop functionality
const uploadArea = document.getElementById('uploadArea');

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--primary)';
    uploadArea.style.background = 'white';
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--gray-300)';
    uploadArea.style.background = 'var(--gray-50)';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--gray-300)';
    uploadArea.style.background = 'var(--gray-50)';
    
    const files = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
    
    if (files.length > 0) {
        const fileInput = document.getElementById('resumeFiles');
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
        handleFileSelection();
    }
});
