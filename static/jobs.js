// Job Market Intelligence Page JavaScript
// No resume upload required - works independently

document.addEventListener('DOMContentLoaded', () => {
    setupFormInteractions();
});

// Analyze job description without resume
async function analyzeJobDescription() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    const targetRole = document.getElementById('targetRole').value.trim();
    const analysisType = document.getElementById('analysisType').value;
    
    if (!jobDescription) {
        if (window.UI) UI.toast('Please enter a job description to analyze', { type: 'info' });
        return;
    }
    
    const analyzeBtn = document.getElementById('analyzeJobBtn');
    const resultsDiv = document.getElementById('atsResults');
    
    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 11-6.219-8.56"/>
        </svg>
        Analyzing...
    `;
    
    resultsDiv.innerHTML = `
        <div class="ats-loading">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 11-6.219-8.56"/>
            </svg>
            Analyzing job description and requirements...
        </div>
    `;
    resultsDiv.style.display = 'block';
    
    try {
        // Call job analysis API (we'll create this)
        const analysis = await analyzeJobRequirements(jobDescription, targetRole, analysisType);
        displayJobAnalysis(analysis);
        
    } catch (error) {
        console.error('Job analysis error:', error);
        resultsDiv.innerHTML = `
            <div class="alert alert-error">
                <strong>Analysis Failed:</strong> ${error.message}
            </div>
        `;
    } finally {
        // Reset button
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd"/>
            </svg>
            Analyze Job Description
        `;
    }
}

// Analyze job requirements using real API
async function analyzeJobRequirements(jobDescription, targetRole, analysisType) {
    const formData = new FormData();
    formData.append('job_description', jobDescription);
    formData.append('target_role', targetRole || '');
    formData.append('analysis_type', analysisType);
    
    const response = await fetch('/analyze-job', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Failed to analyze job description');
    }
    
    const data = await response.json();
    return data.analysis;
}

// Display job analysis results
function displayJobAnalysis(analysis) {
    const resultsDiv = document.getElementById('atsResults');
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    const co = analysis.company_insights || {};
    const mi = analysis.market_insights || {};
    const required = Array.isArray(analysis.required_skills) ? analysis.required_skills : [];
    const preferred = Array.isArray(analysis.preferred_skills) ? analysis.preferred_skills : [];
    const responsibilities = Array.isArray(analysis.key_responsibilities) ? analysis.key_responsibilities : [];
    const atsTips = Array.isArray(analysis.ats_tips) ? analysis.ats_tips : [];
    const topLocations = Array.isArray(mi.top_locations) ? mi.top_locations : [];

    resultsDiv.innerHTML = `
        <div class="job-analysis-results">
            <div class="analysis-section">
                <h4>📋 Role Overview</h4>
                <div class="role-overview">
                    <div class="overview-item"><strong>Position:</strong> ${esc(analysis.role_title || '—')}</div>
                    <div class="overview-item"><strong>Experience Level:</strong> ${esc(analysis.experience_level || '—')}</div>
                    <div class="overview-item"><strong>Salary Range:</strong> ${esc(analysis.salary_range || '—')}</div>
                </div>
            </div>

            <div class="analysis-section">
                <h4>🎯 Skills Requirements</h4>
                <div class="skills-breakdown">
                    <div class="skills-category">
                        <h5>Required Skills</h5>
                        <div class="skills-tags">
                            ${required.length
                                ? required.map(s => `<span class="skill-tag required">${esc(s)}</span>`).join('')
                                : '<span class="hint">No required skills extracted.</span>'}
                        </div>
                    </div>
                    <div class="skills-category">
                        <h5>Preferred Skills</h5>
                        <div class="skills-tags">
                            ${preferred.length
                                ? preferred.map(s => `<span class="skill-tag preferred">${esc(s)}</span>`).join('')
                                : '<span class="hint">No preferred skills extracted.</span>'}
                        </div>
                    </div>
                </div>
            </div>

            <div class="analysis-section">
                <h4>💼 Key Responsibilities</h4>
                <ul class="responsibilities-list">
                    ${responsibilities.length
                        ? responsibilities.map(r => `<li>${esc(r)}</li>`).join('')
                        : '<li class="hint">No responsibilities extracted.</li>'}
                </ul>
            </div>

            <div class="analysis-section">
                <h4>🏢 Company Insights</h4>
                <div class="company-info">
                    <div class="info-item"><strong>Size:</strong> ${esc(co.size || '—')}</div>
                    <div class="info-item"><strong>Culture:</strong> ${esc(co.culture || '—')}</div>
                    <div class="info-item"><strong>Benefits:</strong> ${esc(co.benefits || '—')}</div>
                </div>
            </div>

            <div class="analysis-section">
                <h4>🚀 ATS Optimization Tips</h4>
                <ul class="ats-tips-list">
                    ${atsTips.length
                        ? atsTips.map(t => `<li>${esc(t)}</li>`).join('')
                        : '<li class="hint">No specific tips for this posting.</li>'}
                </ul>
            </div>

            <div class="analysis-section">
                <h4>📊 Market Insights</h4>
                <div class="market-info">
                    <div class="info-item"><strong>Demand:</strong> ${esc(mi.demand || '—')}</div>
                    <div class="info-item"><strong>Growth Outlook:</strong> ${esc(mi.growth_outlook || '—')}</div>
                    <div class="info-item"><strong>Top Locations:</strong> ${esc(topLocations.join(', ') || '—')}</div>
                </div>
            </div>
        </div>
    `;
}

// Get market insights for specific roles
async function getMarketInsights() {
    const jobRole = document.getElementById('jobRole').value.trim();
    const experienceLevel = document.getElementById('experienceLevel').value;
    const industry = document.getElementById('industry').value;
    const location = document.getElementById('location').value.trim();
    
    if (!jobRole) {
        if (window.UI) UI.toast('Please enter a job role to get insights', { type: 'info' });
        return;
    }
    
    const btn = document.getElementById('getInsightsBtn');
    const content = document.getElementById('jobRecommendationsContent');
    
    btn.disabled = true;
    btn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 11-6.219-8.56"/>
        </svg>
        Gathering Insights...
    `;
    
    content.innerHTML = `
        <div class="ats-loading">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 11-6.219-8.56"/>
            </svg>
            Analyzing job market data...
        </div>
    `;
    
    try {
        const insights = await getJobMarketData(jobRole, experienceLevel, industry, location);
        displayMarketInsights(insights);
        
    } catch (error) {
        content.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> ${error.message}
            </div>
        `;
    } finally {
        btn.disabled = false;
        btn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"/>
                <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"/>
            </svg>
            Get Market Insights
        `;
    }
}

// Get job market data using real API
async function getJobMarketData(jobRole, experienceLevel, industry, location) {
    const formData = new FormData();
    formData.append('job_role', jobRole);
    formData.append('experience_level', experienceLevel || '');
    formData.append('industry', industry || '');
    formData.append('location', location || '');
    
    const response = await fetch('/market-insights', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Failed to get market insights');
    }
    
    const data = await response.json();
    return data.insights;
}

// Display market insights
function displayMarketInsights(insights) {
    const content = document.getElementById('jobRecommendationsContent');
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    const sal = insights.salary_data || {};
    const out = insights.job_outlook || {};
    const edu = insights.education_stats || {};
    const top = Array.isArray(insights.top_skills) ? insights.top_skills : [];
    const paths = Array.isArray(insights.career_path) ? insights.career_path : [];
    const companies = Array.isArray(insights.top_companies) ? insights.top_companies : [];
    const fmtSalary = n => (typeof n === 'number') ? '$' + n.toLocaleString() : '—';

    content.innerHTML = `
        <div class="market-insights-results">
            <div class="insights-header">
                <h3>Market Insights for ${esc(insights.role || 'role')}</h3>
                ${insights.experience_level ? `<p>Experience Level: ${esc(insights.experience_level)}</p>` : ''}
                ${insights.notes ? `<p class="hint">${esc(insights.notes)}</p>` : ''}
            </div>

            <div class="insight-card">
                <h4>💰 Salary Information</h4>
                <div class="salary-range">
                    <div class="salary-item"><span class="salary-label">Entry Range:</span> <span class="salary-value">${fmtSalary(sal.min)}</span></div>
                    <div class="salary-item"><span class="salary-label">Median:</span> <span class="salary-value">${fmtSalary(sal.median)}</span></div>
                    <div class="salary-item"><span class="salary-label">Top Range:</span> <span class="salary-value">${fmtSalary(sal.max)}</span></div>
                </div>
            </div>

            <div class="insight-card">
                <h4>📈 Job Market Outlook</h4>
                <div class="market-stats">
                    <div class="stat-item"><strong>Demand:</strong> ${esc(out.demand || '—')}</div>
                    <div class="stat-item"><strong>Growth Rate:</strong> ${esc(out.growth_rate || '—')}</div>
                    <div class="stat-item"><strong>Openings:</strong> ${esc(out.openings || '—')}</div>
                </div>
            </div>

            <div class="insight-card">
                <h4>🎯 Most In-Demand Skills</h4>
                <div class="skills-tags">
                    ${top.length
                        ? top.map(s => `<span class="skill-tag popular">${esc(s)}</span>`).join('')
                        : '<span class="hint">No data available.</span>'}
                </div>
            </div>

            <div class="insight-card">
                <h4>🚀 Career Progression Paths</h4>
                <div class="career-paths">
                    ${paths.length
                        ? paths.map(p => `<div class="career-path">${esc(p)}</div>`).join('')
                        : '<p class="hint">No data available.</p>'}
                </div>
            </div>

            <div class="insight-card">
                <h4>🏢 Top Hiring Companies</h4>
                <div class="companies-list">
                    ${companies.length
                        ? companies.map(c => `<span class="company-tag">${esc(c)}</span>`).join('')
                        : '<span class="hint">No data available.</span>'}
                </div>
            </div>

            <div class="insight-card">
                <h4>🎓 Education Requirements</h4>
                <div class="education-stats">
                    <div class="edu-stat"><strong>${esc(edu.bachelor_required || '—')}</strong> require Bachelor's</div>
                    <div class="edu-stat"><strong>${esc(edu.master_preferred || '—')}</strong> prefer Master's</div>
                    <div class="edu-stat"><strong>${esc(edu.bootcamp_accepted || '—')}</strong> accept bootcamp grads</div>
                </div>
            </div>
        </div>
    `;
}

// Setup form interactions
function setupFormInteractions() {
    // Add keyboard shortcuts
    const jobDescTextarea = document.getElementById('jobDescription');
    if (jobDescTextarea) {
        jobDescTextarea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                analyzeJobDescription();
            }
        });
    }
    
    // Auto-resize textarea
    if (jobDescTextarea) {
        jobDescTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
}