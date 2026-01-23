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
        // Fetch analysis data
        const response = await fetch('/get-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Display resume data if available
            if (data.resume_data) {
                displayResumeData(data.resume_data);
            }
            
            // Display analysis
            if (data.analysis) {
                displayAnalysis(data.analysis);
            }
            
            // Show LinkedIn section
            document.getElementById('linkedinSection').style.display = 'block';
            
            // Show chatbot
            showChatbotFab();
        } else {
            console.error('Failed to load analysis:', data);
            alert('Failed to load analysis data. Please try uploading your resume again.');
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Error loading analysis:', error);
        alert('Error loading analysis data. Please try again.');
        window.location.href = '/';
    }
}

function displayResumeData(data) {
    // Profile Section
    if (data.name || data.email) {
        document.getElementById('candidateName').textContent = data.name || 'Name not found';
        document.getElementById('candidateHeadline').textContent = data.headline || 'Professional';
        document.getElementById('candidateLocation').textContent = data.location || 'Location not specified';
        document.getElementById('candidateEmail').textContent = data.email || 'Email not provided';
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
    const analysisGrid = document.getElementById('analysisGrid');
    analysisGrid.innerHTML = '';
    
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
            key: 'improvement_areas',
            icon: '🎯',
            title: 'Development Areas',
            value: analysis.improvement_areas
        },
        {
            key: 'industry_fit',
            icon: '🏢',
            title: 'Best Fit Industries',
            value: analysis.industry_fit
        },
        {
            key: 'technical_skills_assessment',
            icon: '💻',
            title: 'Technical Skills',
            value: analysis.technical_skills_assessment
        },
        {
            key: 'soft_skills_assessment',
            icon: '🤝',
            title: 'Soft Skills',
            value: analysis.soft_skills_assessment
        },
        {
            key: 'competitive_advantage',
            icon: '🚀',
            title: 'Competitive Advantage',
            value: analysis.competitive_advantage
        },
        {
            key: 'next_career_moves',
            icon: '🎓',
            title: 'Next Career Moves',
            value: analysis.next_career_moves
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
        if (!card.value || card.value === '-' || card.value === '' || 
            card.value.includes('Analysis pending') || 
            card.value.includes('unavailable')) {
            return;
        }
        
        const cardElement = document.createElement('div');
        cardElement.className = `analysis-card ${card.fullWidth ? 'full-width' : ''}`;
        
        let contentHTML = `<p>${card.value}</p>`;
        
        if (card.type === 'score') {
            contentHTML = `
                <div class="analysis-score-badge">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>
                    ${card.value}
                </div>
            `;
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
        alert('Please complete profile building first');
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
