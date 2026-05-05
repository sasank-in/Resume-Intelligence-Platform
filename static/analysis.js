// Get session ID from URL parameter
const urlParams = new URLSearchParams(window.location.search);
let sessionId = urlParams.get('session') || localStorage.getItem('sessionId');
let profileBuilt = false;

// If no session ID, redirect to home
if (!sessionId) {
    window.location.href = '/';
}

// Load analysis data on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadAnalysisData();
});

async function loadAnalysisData() {
    try {
        console.log('[DEBUG] Loading analysis data for session:', sessionId);
        
        // Fetch analysis data
        const response = await fetch('/get-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        console.log('[DEBUG] Response status:', response.status);
        const data = await response.json();
        console.log('[DEBUG] Response data:', data);
        
        if (response.ok) {
            // Display resume data if available
            if (data.resume_data) {
                console.log('[DEBUG] Displaying resume data');
                displayResumeData(data.resume_data);
            }
            
            // Display analysis
            if (data.analysis) {
                console.log('[DEBUG] Displaying analysis');
                displayAnalysis(data.analysis);
            }
            
            // Show LinkedIn section
            document.getElementById('linkedinSection').style.display = 'block';
            
            // Show chatbot
            showChatbotFab();
        } else {
            console.error('Failed to load analysis:', data);
            if (window.UI) UI.toast('Failed to load analysis. Redirecting…', { type: 'error' });
            setTimeout(() => { window.location.href = '/'; }, 1200);
        }
    } catch (error) {
        console.error('Error loading analysis:', error);
        if (window.UI) UI.toast('Error loading analysis. Redirecting…', { type: 'error' });
        setTimeout(() => { window.location.href = '/'; }, 1200);
    }
}

function displayResumeData(data) {
    // Profile Section
    if (data.name || data.email) {
        document.getElementById('candidateName').textContent = data.name || 'Name not found';
        document.getElementById('candidateHeadline').textContent = data.headline || 'Professional';
        document.getElementById('candidateLocation').textContent = data.location || 'Location not specified';
        const emailText = data.email || 'Email not provided';
        document.getElementById('candidateEmail').textContent = emailText;
        const emailWrap = document.getElementById('candidateEmailWrap');
        if (emailWrap) {
            if (data.email) emailWrap.setAttribute('data-copy', data.email);
            else emailWrap.removeAttribute('data-copy');
        }
        document.getElementById('candidateSummary').textContent = data.summary || 'Professional with experience in their field.';
        document.getElementById('profileSection').style.display = 'block';
    }
    
    // Skills Section
    if (data.skills && data.skills.length > 0) {
        const skillsGrid = document.getElementById('skillsGrid');
        skillsGrid.innerHTML = data.skills.map(skill => 
            `<div class="skill-badge">${skill}</div>`
        ).join('');
        document.getElementById('skillsSection').style.display = 'block';
    }
    
    // Experience Timeline
    if (data.experience && data.experience.length > 0) {
        const timeline = document.getElementById('experienceTimeline');
        timeline.innerHTML = data.experience.map(exp => `
            <div class="timeline-item">
                <div class="timeline-date">${exp.duration}</div>
                <div class="timeline-content">
                    <h4>${exp.title}</h4>
                    <p class="company">${exp.company}</p>
                    ${exp.highlights && exp.highlights.length > 0 ? `
                        <ul class="highlights">
                            ${exp.highlights.map(h => `<li>${h}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>
            </div>
        `).join('');
        document.getElementById('experienceSection').style.display = 'block';
    }
    
    // Education Section
    if (data.education && data.education.length > 0) {
        const educationGrid = document.getElementById('educationGrid');
        educationGrid.innerHTML = data.education.map(edu => `
            <div class="education-card">
                <h4>${edu.degree}</h4>
                <p class="institution">${edu.institution}</p>
                <p class="year">${edu.year}</p>
                ${edu.details ? `<p class="details">${edu.details}</p>` : ''}
            </div>
        `).join('');
        document.getElementById('educationSection').style.display = 'block';
    }
}

function displayAnalysis(analysis) {
    try {
        console.log('[DEBUG] displayAnalysis called with:', analysis);
        const analysisGrid = document.getElementById('analysisGrid');
        analysisGrid.innerHTML = '';
        
        // Helper function to combine Development Areas and Next Career Moves
        function combineDevAndCareerMoves(improvementAreas, nextCareerMoves) {
            if (!improvementAreas && !nextCareerMoves) return null;
            
            let combined = '';
            
            // Handle improvement areas (can be string or array)
            if (improvementAreas) {
                let areasText = '';
                if (Array.isArray(improvementAreas)) {
                    areasText = improvementAreas.join(', ');
                } else if (typeof improvementAreas === 'string' && improvementAreas.trim() && improvementAreas !== '-') {
                    areasText = improvementAreas;
                }
                
                if (areasText) {
                    combined += `<div class="merged-section"><h4 class="merged-subtitle">🎯 Development Areas</h4><p>${areasText}</p></div>`;
                }
            }
            
            // Handle next career moves (can be string or array)
            if (nextCareerMoves) {
                let movesText = '';
                if (Array.isArray(nextCareerMoves)) {
                    movesText = nextCareerMoves.join(', ');
                } else if (typeof nextCareerMoves === 'string' && nextCareerMoves.trim() && nextCareerMoves !== '-') {
                    movesText = nextCareerMoves;
                }
                
                if (movesText) {
                    if (combined) combined += '<div class="section-divider"></div>';
                    combined += `<div class="merged-section"><h4 class="merged-subtitle">🚀 Next Career Moves</h4><p>${movesText}</p></div>`;
                }
            }
            
            return combined || null;
        }
    
    const analysisCards = [
        {
            key: 'overall_score',
            icon: '⭐',
            title: 'Overall Assessment',
            value: analysis.overall_score,
            type: 'score'
        },
        {
            key: 'career_trajectory',
            icon: '📈',
            title: 'Career Trajectory',
            value: analysis.career_trajectory
        },
        {
            key: 'key_strengths',
            icon: '💪',
            title: 'Core Strengths',
            value: analysis.key_strengths
        },
        {
            key: 'development_and_career_moves',
            icon: '🎯',
            title: 'Development Areas & Next Career Moves',
            value: combineDevAndCareerMoves(analysis.improvement_areas, analysis.next_career_moves) || 'Development areas and career moves analysis',
            fullWidth: true
        },
        {
            key: 'industry_fit',
            icon: '🏢',
            title: 'Best Fit Industries',
            value: analysis.industry_fit
        },
        {
            key: 'competitive_advantage',
            icon: '🚀',
            title: 'Competitive Advantage',
            value: analysis.competitive_advantage
        },
        {
            key: 'salary_expectations',
            icon: '💰',
            title: 'Salary Insights',
            value: analysis.salary_expectations
        },
        {
            key: 'recommendations_summary',
            icon: '💡',
            title: 'Comprehensive Recommendations',
            value: analysis.recommendations_summary,
            fullWidth: true
        }
    ];
    
    analysisCards.forEach(card => {
        console.log('[DEBUG] Processing card:', card.key, 'value:', card.value);
        
        if (!card.value || card.value === '-' || card.value === '' || 
            (typeof card.value === 'string' && (card.value.includes('Analysis pending') || card.value.includes('unavailable')))) {
            console.log('[DEBUG] Skipping card:', card.key);
            return;
        }
        
        const cardElement = document.createElement('div');
        cardElement.className = `analysis-card ${card.fullWidth ? 'full-width' : ''}`;
        
        let contentHTML = '';
        
        if (card.type === 'score') {
            contentHTML = `
                <div class="analysis-score-badge">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                    ${card.value}
                </div>
            `;
        } else if (card.key === 'development_and_career_moves') {
            // For merged card, value already contains HTML
            contentHTML = card.value;
        } else {
            contentHTML = `<p>${card.value}</p>`;
        }
        
        cardElement.innerHTML = `
            <div class="analysis-card-header">
                <div class="analysis-icon">${card.icon}</div>
                <h3>${card.title}</h3>
            </div>
            <div class="analysis-card-content">
                ${contentHTML}
            </div>
        `;
        
        analysisGrid.appendChild(cardElement);
    });
    
    if (analysisGrid.children.length > 0) {
        document.getElementById('analysisSection').style.display = 'block';
    }

    // Professional Summary
    const suggestedJob = analysis.suggested_job_summary;
    const suggestedJobSection = document.getElementById('suggestedJobSection');
    const suggestedJobSummaryEl = document.getElementById('suggestedJobSummary');
    
    if (suggestedJob && suggestedJob.trim() && suggestedJob !== '-' && 
        !suggestedJob.includes('pending') && !suggestedJob.includes('unavailable')) {
        suggestedJobSummaryEl.textContent = suggestedJob;
        suggestedJobSection.style.display = 'block';
    }
    
    console.log('[DEBUG] displayAnalysis completed successfully');
    } catch (error) {
        console.error('[ERROR] displayAnalysis failed:', error);
        console.error('[ERROR] Stack:', error.stack);
        throw error;
    }
}

// Chatbot functionality
function toggleChatbot() {
    const modal = document.getElementById('chatbotModal');
    if (!modal) return;
    
    modal.classList.toggle('open');
    
    if (modal.classList.contains('open')) {
        setTimeout(() => {
            const input = document.getElementById('chatbotInput');
            if (input) input.focus();
        }, 300);
    }
}

function closeChatbot() {
    const modal = document.getElementById('chatbotModal');
    if (modal) {
        modal.classList.remove('open');
    }
}

function minimizeChatbot() {
    closeChatbot();
}

function showChatbotFab() {
    const chatbotBtn = document.getElementById('chatbotBtn');
    if (chatbotBtn) {
        chatbotBtn.classList.add('show');
    }
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbotMessages');
    if (!messagesContainer) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-typing';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = '<span></span><span></span><span></span>';
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

async function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesContainer = document.getElementById('chatbotMessages');
    const sendButton = document.querySelector('.chatbot-send');
    
    const welcomeMsg = messagesContainer.querySelector('.chatbot-welcome');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const userMsg = document.createElement('div');
    userMsg.className = 'chatbot-message user';
    userMsg.innerHTML = `${message}<span class="message-time">${getCurrentTime()}</span>`;
    messagesContainer.appendChild(userMsg);
    
    input.value = '';
    input.disabled = true;
    sendButton.disabled = true;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    showTypingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        hideTypingIndicator();
        
        const data = await response.json();
        
        if (response.ok) {
            const aiMsg = document.createElement('div');
            aiMsg.className = 'chatbot-message ai';
            aiMsg.innerHTML = `${data.response}<span class="message-time">${getCurrentTime()}</span>`;
            messagesContainer.appendChild(aiMsg);
        } else {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chatbot-message ai error';
            errorMsg.innerHTML = `⚠️ ${data.detail || 'Could not get response'}<span class="message-time">${getCurrentTime()}</span>`;
            messagesContainer.appendChild(errorMsg);
        }
    } catch (error) {
        hideTypingIndicator();
        const errorMsg = document.createElement('div');
        errorMsg.className = 'chatbot-message ai error';
        errorMsg.innerHTML = `⚠️ Error connecting to server<span class="message-time">${getCurrentTime()}</span>`;
        messagesContainer.appendChild(errorMsg);
    } finally {
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function sendQuickMessage(message) {
    const input = document.getElementById('chatbotInput');
    if (!input) return;
    
    input.value = message;
    sendChatbotMessage();
}

document.addEventListener('DOMContentLoaded', () => {
    const chatbotInput = document.getElementById('chatbotInput');
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatbotMessage();
        });
    }
});

// LinkedIn Profile Functions
async function addLinkedInProfile() {
    const linkedinUrl = document.getElementById('linkedinUrl').value.trim();
    const statusEl = document.getElementById('linkedinStatus');
    
    if (!linkedinUrl) {
        statusEl.textContent = '⚠️ Please enter a LinkedIn profile URL';
        statusEl.className = 'linkedin-status error';
        return;
    }
    
    if (!linkedinUrl.includes('linkedin.com')) {
        statusEl.textContent = '⚠️ Please enter a valid LinkedIn URL';
        statusEl.className = 'linkedin-status error';
        return;
    }
    
    statusEl.textContent = '🔄 Extracting LinkedIn profile...';
    statusEl.className = 'linkedin-status';
    
    try {
        const response = await fetch('/add-linkedin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                linkedin_url: linkedinUrl,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            statusEl.textContent = '✓ LinkedIn profile added successfully!';
            statusEl.className = 'linkedin-status success';
            if (window.UI) UI.toast('LinkedIn profile merged', { type: 'success' });
            
            if (data.unified_profile) {
                displayResumeData(data.unified_profile);
            }
            
            profileBuilt = true;
            
            setTimeout(() => {
                document.getElementById('linkedinSection').style.display = 'none';
                document.getElementById('jobRecommendationsSection').style.display = 'block';
            }, 1500);
        } else {
            statusEl.textContent = '❌ ' + (data.detail || 'Failed to extract LinkedIn profile');
            statusEl.className = 'linkedin-status error';
        }
    } catch (error) {
        console.error('LinkedIn error:', error);
        statusEl.textContent = '❌ Error: ' + error.message;
        statusEl.className = 'linkedin-status error';
    }
}

async function skipLinkedIn() {
    const statusEl = document.getElementById('linkedinStatus');
    statusEl.textContent = '⏭️ Building profile from resume only...';
    statusEl.className = 'linkedin-status';
    
    try {
        const response = await fetch('/skip-linkedin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            statusEl.textContent = '✓ Profile created from resume';
            statusEl.className = 'linkedin-status success';
            
            profileBuilt = true;
            
            setTimeout(() => {
                document.getElementById('linkedinSection').style.display = 'none';
                document.getElementById('jobRecommendationsSection').style.display = 'block';
            }, 1000);
        } else {
            statusEl.textContent = '❌ ' + (data.detail || 'Failed to build profile');
            statusEl.className = 'linkedin-status error';
        }
    } catch (error) {
        console.error('Skip LinkedIn error:', error);
        statusEl.textContent = '❌ Error: ' + error.message;
        statusEl.className = 'linkedin-status error';
    }
}

// Job Recommendations
async function getJobRecommendations() {
    if (!profileBuilt) {
        if (window.UI) UI.toast('Please complete profile building first', { type: 'info' });
        return;
    }
    
    const btn = document.getElementById('getRecommendationsBtn');
    const contentEl = document.getElementById('jobRecommendationsContent');
    
    btn.disabled = true;
    btn.textContent = '🔄 Generating recommendations...';
    contentEl.innerHTML = '<div class="loading"><div class="spinner"></div><p>Analyzing your profile and matching with jobs...</p></div>';
    
    try {
        const response = await fetch('/recommend-jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayJobRecommendations(data.recommendations);
            btn.style.display = 'none';
        } else {
            contentEl.innerHTML = `<div class="error-message">❌ ${data.detail || 'Failed to generate recommendations'}</div>`;
            btn.disabled = false;
            btn.textContent = 'Try Again';
        }
    } catch (error) {
        console.error('Job recommendations error:', error);
        contentEl.innerHTML = `<div class="error-message">❌ Error: ${error.message}</div>`;
        btn.disabled = false;
        btn.textContent = 'Try Again';
    }
}

function displayJobRecommendations(data) {
    const contentEl = document.getElementById('jobRecommendationsContent');
    
    if (!data || !data.recommendations || data.recommendations.length === 0) {
        contentEl.innerHTML = '<p>No recommendations available</p>';
        return;
    }
    
    let html = '<div class="job-recommendations-grid">';
    
    data.recommendations.forEach((job, index) => {
        html += `
            <div class="job-card">
                <div class="job-header">
                    <h3>${job.job_title}</h3>
                    <div class="match-score" style="background: linear-gradient(135deg, #1e40af ${job.match_score}%, #ddd ${job.match_score}%);">
                        ${job.match_score}% Match
                    </div>
                </div>
                <p class="company-type">🏢 ${job.company_type}</p>
                <p class="job-reasoning">${job.reasoning}</p>
                
                <div class="job-details">
                    <div class="job-section">
                        <h4>✅ Matching Skills</h4>
                        <div class="skills-tags">
                            ${job.matching_skills.map(s => `<span class="skill-tag match">${s}</span>`).join('')}
                        </div>
                    </div>
                    
                    ${job.skill_gaps && job.skill_gaps.length > 0 ? `
                        <div class="job-section">
                            <h4>📚 Skills to Develop</h4>
                            <div class="skills-tags">
                                ${job.skill_gaps.map(s => `<span class="skill-tag gap">${s}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="job-footer">
                        <span class="salary">💰 ${job.salary_range}</span>
                        <span class="growth">📈 ${job.growth_potential}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    if (data.career_insights) {
        html += `
            <div class="career-insights">
                <h3>💡 Career Insights</h3>
                <div class="insights-grid">
                    <div class="insight-card">
                        <h4>🌟 Strongest Areas</h4>
                        <p>${data.career_insights.strongest_areas}</p>
                    </div>
                    <div class="insight-card">
                        <h4>🏭 Recommended Industries</h4>
                        <div class="industry-tags">
                            ${data.career_insights.recommended_industries.map(i => `<span class="industry-tag">${i}</span>`).join('')}
                        </div>
                    </div>
                    <div class="insight-card">
                        <h4>🚀 Next Level Roles</h4>
                        <ul>
                            ${data.career_insights.next_level_roles.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="insight-card">
                        <h4>📖 Priority Skills to Learn</h4>
                        <ul>
                            ${data.career_insights.skill_development_priority.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
    
    contentEl.innerHTML = html;
}
// ATS Checker Functions
async function checkATSCompatibility() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    const targetRole = document.getElementById('targetRole').value.trim();
    const atsSystem = document.getElementById('atsSystem').value;
    
    if (!jobDescription) {
        if (window.UI) UI.toast('Please enter a job description', { type: 'info' });
        return;
    }
    
    const checkBtn = document.getElementById('checkATSBtn');
    const resultsDiv = document.getElementById('atsResults');
    
    // Show loading state
    checkBtn.disabled = true;
    checkBtn.innerHTML = `
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
            Analyzing ATS compatibility...
        </div>
    `;
    resultsDiv.style.display = 'block';
    
    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('job_description', jobDescription);
        formData.append('target_role', targetRole);
        formData.append('ats_system', atsSystem);
        
        const response = await fetch('/check-ats', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayATSResults(data.analysis);
        } else {
            throw new Error(data.detail || 'ATS analysis failed');
        }
    } catch (error) {
        console.error('ATS analysis error:', error);
        resultsDiv.innerHTML = `
            <div class="alert alert-error">
                <strong>Analysis Failed:</strong> ${error.message}
            </div>
        `;
    } finally {
        // Reset button
        checkBtn.disabled = false;
        checkBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            Check ATS Compatibility
        `;
    }
}

function displayATSResults(analysis) {
    const resultsDiv = document.getElementById('atsResults');
    const score = analysis.overall_score;
    const scoreClass = getScoreClass(score);
    
    resultsDiv.innerHTML = `
        <!-- ATS Score Card -->
        <div class="ats-score-card">
            <div class="ats-score-value">${score}%</div>
            <div class="ats-score-label">ATS Compatibility Score</div>
            <div class="ats-score-description">${analysis.pass_probability.message}</div>
        </div>
        
        <!-- Analysis Grid -->
        <div class="ats-analysis-grid">
            <!-- Keyword Analysis -->
            <div class="ats-analysis-card">
                <div class="ats-analysis-header">
                    <div class="ats-analysis-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
                        </svg>
                    </div>
                    <div class="ats-analysis-title">Keywords</div>
                </div>
                <div class="ats-score-bar">
                    <div class="ats-score-fill ${getScoreClass(analysis.keyword_analysis.keyword_score)}" 
                         style="width: ${analysis.keyword_analysis.keyword_score}%"></div>
                </div>
                <p><strong>Required Skills Match:</strong> ${analysis.keyword_analysis.required_skill_coverage.toFixed(1)}%</p>
                <p><strong>Matching Skills:</strong> ${analysis.keyword_analysis.required_skill_matches.slice(0, 5).join(', ') || 'None'}</p>
                ${analysis.keyword_analysis.missing_required_skills.length > 0 ? 
                    `<p><strong>Missing:</strong> ${analysis.keyword_analysis.missing_required_skills.slice(0, 5).join(', ')}</p>` : ''}
            </div>
            
            <!-- Format Analysis -->
            <div class="ats-analysis-card">
                <div class="ats-analysis-header">
                    <div class="ats-analysis-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <div class="ats-analysis-title">Format</div>
                </div>
                <div class="ats-score-bar">
                    <div class="ats-score-fill ${getScoreClass(analysis.format_analysis.format_score)}" 
                         style="width: ${analysis.format_analysis.format_score}%"></div>
                </div>
                <p><strong>ATS-Friendly Elements:</strong> ${analysis.format_analysis.ats_friendly_elements.length}</p>
                ${analysis.format_analysis.issues.length > 0 ? 
                    `<p><strong>Issues:</strong> ${analysis.format_analysis.issues.slice(0, 3).join(', ')}</p>` : 
                    '<p><strong>Status:</strong> No major format issues detected</p>'}
            </div>
            
            <!-- Structure Analysis -->
            <div class="ats-analysis-card">
                <div class="ats-analysis-header">
                    <div class="ats-analysis-icon">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 11H5m14-7H5m14 14H5"/>
                        </svg>
                    </div>
                    <div class="ats-analysis-title">Structure</div>
                </div>
                <div class="ats-score-bar">
                    <div class="ats-score-fill ${getScoreClass(analysis.structure_analysis.structure_score)}" 
                         style="width: ${analysis.structure_analysis.structure_score}%"></div>
                </div>
                <p><strong>Section Order:</strong> ${analysis.structure_analysis.section_order.join(' → ')}</p>
                <p><strong>Consistency:</strong> ${analysis.structure_analysis.consistency_score.toFixed(1)}%</p>
            </div>
        </div>
        
        <!-- Competitive Analysis -->
        <div class="ats-analysis-card" style="margin-bottom: 2rem;">
            <div class="ats-analysis-header">
                <div class="ats-analysis-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>
                </div>
                <div class="ats-analysis-title">Competitive Position</div>
            </div>
            <p><strong>Your Position:</strong> ${analysis.competitive_analysis.percentile} of candidates</p>
            <p><strong>Pass Probability:</strong> ${analysis.pass_probability.probability}</p>
            <p><strong>Industry Benchmark:</strong> ${analysis.competitive_analysis.benchmark_score}%</p>
        </div>
        
        <!-- Recommendations -->
        <div class="ats-recommendations">
            <h4>Improvement Recommendations</h4>
            ${analysis.recommendations.map(rec => `
                <div class="recommendation-item">
                    <div class="recommendation-header">
                        <span class="priority-badge ${rec.priority.toLowerCase()}">${rec.priority}</span>
                        <span class="recommendation-category">${rec.category}</span>
                    </div>
                    <div class="recommendation-issue">${rec.issue}</div>
                    <div class="recommendation-action">${rec.action}</div>
                    <div class="recommendation-impact">Impact: ${rec.impact}</div>
                </div>
            `).join('')}
        </div>
    `;
}

function getScoreClass(score) {
    if (score >= 85) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 60) return 'fair';
    return 'poor';
}

// Add event listener for Enter key in job description textarea
document.addEventListener('DOMContentLoaded', () => {
    const jobDescTextarea = document.getElementById('jobDescription');
    if (jobDescTextarea) {
        jobDescTextarea.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                checkATSCompatibility();
            }
        });
    }
});