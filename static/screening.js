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
        alert('Please select at least one resume PDF');
        return;
    }
    
    const jobRequirements = getJobRequirements();
    
    if (!jobRequirements.job_title) {
        alert('Please enter a job title');
        return;
    }
    
    if (jobRequirements.required_skills.length === 0) {
        alert('Please enter at least one required skill');
        return;
    }
    
    // Show loading overlay
    const loadingOverlay = document.getElementById('loadingOverlay');
    const progressText = document.getElementById('progressText');
    loadingOverlay.style.display = 'flex';
    progressText.textContent = `Processing ${selectedFiles.length} resume(s)...`;
    
    try {
        // Prepare form data
        const formData = new FormData();
        
        // Add all files
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        // Add job requirements as JSON string
        formData.append('job_requirements', JSON.stringify(jobRequirements));
        
        // Send request
        const response = await fetch('/screening/screen-batch', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            displayResults(data);
        } else {
            throw new Error(data.detail || 'Screening failed');
        }
    } catch (error) {
        console.error('Screening error:', error);
        alert('Error: ' + error.message);
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const summaryStats = document.getElementById('summaryStats');
    const topCandidates = document.getElementById('topCandidates');
    
    resultsSection.style.display = 'block';
    
    // Display summary statistics
    const summary = data.summary;
    summaryStats.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${summary.total_processed}</div>
            <div class="stat-label">Total Processed</div>
        </div>
        <div class="stat-item highlight">
            <div class="stat-value">${summary.highly_recommended}</div>
            <div class="stat-label">Highly Recommended</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${summary.recommended}</div>
            <div class="stat-label">Recommended</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${summary.maybe}</div>
            <div class="stat-label">Maybe</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${summary.average_score.toFixed(1)}</div>
            <div class="stat-label">Average Score</div>
        </div>
    `;
    
    // Display top candidates
    if (data.top_candidates && data.top_candidates.length > 0) {
        topCandidates.innerHTML = `
            <h3 style="margin-bottom: 1.5rem; font-size: 1.5rem; font-weight: 700;">Top Candidates</h3>
            <div class="job-recommendations-grid">
                ${data.top_candidates.map(candidate => createCandidateCard(candidate)).join('')}
            </div>
        `;
    } else {
        topCandidates.innerHTML = '<p>No candidates found matching the criteria.</p>';
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function createCandidateCard(candidate) {
    const statusColors = {
        'HIGHLY_RECOMMENDED': '#10b981',
        'RECOMMENDED': '#3b82f6',
        'MAYBE': '#f59e0b',
        'NOT_RECOMMENDED': '#ef4444'
    };
    
    const statusColor = statusColors[candidate.status] || '#6b7280';
    
    return `
        <div class="job-card">
            <div class="job-header">
                <div>
                    <h3 style="margin-bottom: 0.5rem;">Rank #${candidate.rank}: ${candidate.name || 'N/A'}</h3>
                    <p style="color: var(--gray-600); font-size: 0.875rem;">
                        ${candidate.email || 'No email'} | ${candidate.phone || 'No phone'}
                    </p>
                </div>
                <div class="match-score" style="background: ${statusColor};">
                    ${candidate.score}/100
                </div>
            </div>
            
            <div style="margin: 1rem 0;">
                <span style="display: inline-block; padding: 0.375rem 0.75rem; background: ${statusColor}20; color: ${statusColor}; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600;">
                    ${candidate.status.replace(/_/g, ' ')}
                </span>
            </div>
            
            ${candidate.key_strengths && candidate.key_strengths.length > 0 ? `
                <div class="job-section">
                    <h4>Key Strengths</h4>
                    <div class="skills-tags">
                        ${candidate.key_strengths.map(skill => 
                            `<span class="skill-tag match">${skill}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

function loadTemplate() {
    fetch('/screening/job-requirements-template')
        .then(response => response.json())
        .then(template => {
            document.getElementById('jobTitle').value = template.job_title;
            document.getElementById('requiredSkills').value = template.required_skills.join(', ');
            document.getElementById('preferredSkills').value = template.preferred_skills.join(', ');
            document.getElementById('minExperience').value = template.min_experience_years;
            document.getElementById('maxExperience').value = template.max_experience_years;
            document.getElementById('requiredDegree').value = template.required_degree || '';
            
            alert('Template loaded successfully!');
        })
        .catch(error => {
            console.error('Error loading template:', error);
            alert('Failed to load template');
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
