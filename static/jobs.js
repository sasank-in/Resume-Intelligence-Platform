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
        alert('Please enter a job description to analyze');
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
    
    resultsDiv.innerHTML = `
        <div class="job-analysis-results">
            <!-- Role Overview -->
            <div class="analysis-section">
                <h4>📋 Role Overview</h4>
                <div class="role-overview">
                    <div class="overview-item">
                        <strong>Position:</strong> ${analysis.role_title}
                    </div>
                    <div class="overview-item">
                        <strong>Experience Level:</strong> ${analysis.experience_level}
                    </div>
                    <div class="overview-item">
                        <strong>Salary Range:</strong> ${analysis.salary_range}
                    </div>
                </div>
            </div>
            
            <!-- Skills Breakdown -->
            <div class="analysis-section">
                <h4>🎯 Skills Requirements</h4>
                <div class="skills-breakdown">
                    <div class="skills-category">
                        <h5>Required Skills</h5>
                        <div class="skills-tags">
                            ${analysis.required_skills.map(skill => 
                                `<span class="skill-tag required">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="skills-category">
                        <h5>Preferred Skills</h5>
                        <div class="skills-tags">
                            ${analysis.preferred_skills.map(skill => 
                                `<span class="skill-tag preferred">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Key Responsibilities -->
            <div class="analysis-section">
                <h4>💼 Key Responsibilities</h4>
                <ul class="responsibilities-list">
                    ${analysis.key_responsibilities.map(resp => 
                        `<li>${resp}</li>`
                    ).join('')}
                </ul>
            </div>
            
            <!-- Company Insights -->
            <div class="analysis-section">
                <h4>🏢 Company Insights</h4>
                <div class="company-info">
                    <div class="info-item">
                        <strong>Company Size:</strong> ${analysis.company_insights.size}
                    </div>
                    <div class="info-item">
                        <strong>Culture:</strong> ${analysis.company_insights.culture}
                    </div>
                    <div class="info-item">
                        <strong>Benefits:</strong> ${analysis.company_insights.benefits}
                    </div>
                </div>
            </div>
            
            <!-- ATS Optimization Tips -->
            <div class="analysis-section">
                <h4>🚀 ATS Optimization Tips</h4>
                <ul class="ats-tips-list">
                    ${analysis.ats_tips.map(tip => 
                        `<li>${tip}</li>`
                    ).join('')}
                </ul>
            </div>
            
            <!-- Market Insights -->
            <div class="analysis-section">
                <h4>📊 Market Insights</h4>
                <div class="market-info">
                    <div class="info-item">
                        <strong>Market Demand:</strong> ${analysis.market_insights.demand}
                    </div>
                    <div class="info-item">
                        <strong>Growth Outlook:</strong> ${analysis.market_insights.growth_outlook}
                    </div>
                    <div class="info-item">
                        <strong>Top Locations:</strong> ${analysis.market_insights.top_locations.join(', ')}
                    </div>
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
        alert('Please enter a job role to get insights');
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
    
    content.innerHTML = `
        <div class="market-insights-results">
            <div class="insights-header">
                <h3>Market Insights for ${insights.role}</h3>
                ${insights.experience_level ? `<p>Experience Level: ${insights.experience_level}</p>` : ''}
            </div>
            
            <!-- Salary Information -->
            <div class="insight-card">
                <h4>💰 Salary Information</h4>
                <div class="salary-range">
                    <div class="salary-item">
                        <span class="salary-label">Entry Range:</span>
                        <span class="salary-value">$${insights.salary_data.min.toLocaleString()}</span>
                    </div>
                    <div class="salary-item">
                        <span class="salary-label">Median:</span>
                        <span class="salary-value">$${insights.salary_data.median.toLocaleString()}</span>
                    </div>
                    <div class="salary-item">
                        <span class="salary-label">Top Range:</span>
                        <span class="salary-value">$${insights.salary_data.max.toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <!-- Job Market Outlook -->
            <div class="insight-card">
                <h4>📈 Job Market Outlook</h4>
                <div class="market-stats">
                    <div class="stat-item">
                        <strong>Demand:</strong> ${insights.job_outlook.demand}
                    </div>
                    <div class="stat-item">
                        <strong>Growth Rate:</strong> ${insights.job_outlook.growth_rate} annually
                    </div>
                    <div class="stat-item">
                        <strong>Available Positions:</strong> ${insights.job_outlook.openings}
                    </div>
                </div>
            </div>
            
            <!-- Top Skills -->
            <div class="insight-card">
                <h4>🎯 Most In-Demand Skills</h4>
                <div class="skills-tags">
                    ${insights.top_skills.map(skill => 
                        `<span class="skill-tag popular">${skill}</span>`
                    ).join('')}
                </div>
            </div>
            
            <!-- Career Progression -->
            <div class="insight-card">
                <h4>🚀 Career Progression Paths</h4>
                <div class="career-paths">
                    ${insights.career_path.map(path => 
                        `<div class="career-path">${path}</div>`
                    ).join('')}
                </div>
            </div>
            
            <!-- Top Employers -->
            <div class="insight-card">
                <h4>🏢 Top Hiring Companies</h4>
                <div class="companies-list">
                    ${insights.top_companies.map(company => 
                        `<span class="company-tag">${company}</span>`
                    ).join('')}
                </div>
            </div>
            
            <!-- Education Requirements -->
            <div class="insight-card">
                <h4>🎓 Education Requirements</h4>
                <div class="education-stats">
                    <div class="edu-stat">
                        <strong>${insights.education_stats.bachelor_required}</strong> require Bachelor's degree
                    </div>
                    <div class="edu-stat">
                        <strong>${insights.education_stats.master_preferred}</strong> prefer Master's degree
                    </div>
                    <div class="edu-stat">
                        <strong>${insights.education_stats.bootcamp_accepted}</strong> accept bootcamp graduates
                    </div>
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