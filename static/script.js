let sessionId = Date.now().toString();
let profileBuilt = false;

document.getElementById('resumeFile').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    document.getElementById('fileName').textContent = `Selected: ${file.name}`;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('status').textContent = '';
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);
    
    try {
        console.log('Uploading file:', file.name, 'Session ID:', sessionId);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        console.log('Upload response status:', response.status);
        
        const data = await response.json();
        console.log('Upload response data:', data);
        
        const statusEl = document.getElementById('status');
        
        if (response.ok) {
            statusEl.textContent = '✓ Resume analyzed successfully!';
            statusEl.className = 'status success';
            statusEl.style.display = 'block';
            
            // Display resume data
            displayResumeData(data.resume_data);
            
            // Show LinkedIn section
            document.getElementById('linkedinSection').style.display = 'block';
            
            // Get detailed analysis
            await getDetailedAnalysis();
        } else {
            statusEl.textContent = 'Error: ' + (data.detail || 'Failed to upload resume');
            statusEl.className = 'status error';
            statusEl.style.display = 'block';
            console.error('Upload error:', data);
        }
    } catch (error) {
        console.error('Upload error details:', error);
        document.getElementById('status').textContent = '❌ Error uploading resume: ' + error.message;
        document.getElementById('status').className = 'status error';
        document.getElementById('status').style.display = 'block';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

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

    // Certifications & Languages
    let hasCerts = data.certifications && data.certifications.length > 0;
    let hasLangs = data.languages && data.languages.length > 0;
    
    if (hasCerts || hasLangs) {
        if (hasCerts) {
            document.getElementById('certificationsList').innerHTML = data.certifications
                .map(cert => `<li>${cert}</li>`)
                .join('');
            document.getElementById('certificationsBox').style.display = 'block';
        }
        
        if (hasLangs) {
            document.getElementById('languagesList').innerHTML = data.languages
                .map(lang => `<li>${lang}</li>`)
                .join('');
            document.getElementById('languagesBox').style.display = 'block';
        }
        
        document.getElementById('certificationsLanguagesSection').style.display = 'block';
    }

    // Strengths & Recommendations from resume data
    let hasStrengths = data.strengths && data.strengths.length > 0;
    let hasRecommendations = data.recommendations && data.recommendations.length > 0;
    
    if (hasStrengths || hasRecommendations) {
        if (hasStrengths) {
            document.getElementById('strengthsList').innerHTML = data.strengths
                .map(strength => `<li>${strength}</li>`)
                .join('');
            document.getElementById('strengthsBox').style.display = 'block';
        }
        
        if (hasRecommendations) {
            document.getElementById('recommendationsList').innerHTML = data.recommendations
                .map(rec => `<li>${rec}</li>`)
                .join('');
            document.getElementById('recommendationsBox').style.display = 'block';
        }
        
        document.getElementById('resumeDetailsSection').style.display = 'block';
    }

    // Show chatbot FAB
    showChatbotFab();
}

async function getDetailedAnalysis() {
    try {
        const response = await fetch('/get-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (response.ok && data.analysis) {
            displayAnalysis(data.analysis);
        } else {
            console.log('Analysis error:', data);
            console.log('Status:', response.status);
            // Still show what we have even if analysis fails
            displayAnalysis({
                overall_score: "Analysis pending...",
                career_trajectory: "Analyzing your career path...",
                key_strengths: "Identifying strengths...",
                improvement_areas: "Checking improvement areas...",
                industry_fit: "Analyzing industry fit...",
                technical_skills_assessment: "Evaluating technical skills...",
                soft_skills_assessment: "Evaluating soft skills...",
                achievement_highlights: "Reviewing achievements...",
                gap_analysis: "Finding gaps...",
                salary_expectations: "Estimating salary...",
                next_career_moves: "Planning next steps...",
                competitive_advantage: "Assessing advantages...",
                interview_talking_points: "Preparing talking points...",
                recommendations_summary: "Generating recommendations..."
            });
        }
    } catch (error) {
        console.log('Analysis fetch error:', error);
        // Show placeholder if fetch fails
        displayAnalysis({
            overall_score: "Analysis unavailable",
            career_trajectory: "Please refresh and try again",
            key_strengths: "-",
            improvement_areas: "-",
            industry_fit: "-",
            technical_skills_assessment: "-",
            soft_skills_assessment: "-",
            achievement_highlights: "-",
            gap_analysis: "-",
            salary_expectations: "-",
            next_career_moves: "-",
            competitive_advantage: "-",
            interview_talking_points: "-",
            recommendations_summary: "-"
        });
    }
}

function displayAnalysis(analysis) {
    const analysisGrid = document.getElementById('analysisGrid');
    analysisGrid.innerHTML = ''; // Clear previous content
    
    // Define analysis cards with their properties
    const analysisCards = [
        {
            key: 'overall_score',
            icon: '⭐',
            title: 'Overall Assessment',
            value: analysis.overall_score
        },
        {
            key: 'career_trajectory',
            icon: '💼',
            title: 'Career Trajectory',
            value: analysis.career_trajectory
        },
        {
            key: 'key_strengths',
            icon: '✨',
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
            key: 'next_career_moves',
            icon: '🎓',
            title: 'Next Career Moves',
            value: analysis.next_career_moves
        },
        {
            key: 'recommendations_summary',
            icon: '💡',
            title: 'Comprehensive Recommendations',
            value: analysis.recommendations_summary,
            fullWidth: true
        }
    ];
    
    // Generate cards only for fields with data
    analysisCards.forEach(card => {
        // Skip if value is missing, empty, or is a placeholder
        if (!card.value || card.value === '-' || card.value === '') {
            return;
        }
        
        const cardElement = document.createElement('div');
        cardElement.className = `analysis-card ${card.fullWidth ? 'full-width' : ''}`;
        
        cardElement.innerHTML = `
            <h3>${card.icon} ${card.title}</h3>
            <p>${card.value}</p>
        `;
        
        analysisGrid.appendChild(cardElement);
    });
    
    // Only show section if there are cards to display
    if (analysisGrid.children.length > 0) {
        document.getElementById('analysisSection').style.display = 'block';
    }

    // Suggested Job Summary rendering
    const suggestedJob = analysis.suggested_job_summary;
    const suggestedJobSection = document.getElementById('suggestedJobSection');
    const suggestedJobSummaryEl = document.getElementById('suggestedJobSummary');
    if (suggestedJob && suggestedJob.trim() && suggestedJob !== '-') {
        suggestedJobSummaryEl.textContent = suggestedJob;
        suggestedJobSection.style.display = 'block';
    }
}

// Chatbot modal functionality
function toggleChatbot() {
    const modal = document.getElementById('chatbotModal');
    modal.classList.toggle('open');
    
    // Focus input when opened
    if (modal.classList.contains('open')) {
        setTimeout(() => {
            document.getElementById('chatbotInput').focus();
        }, 300);
    }
}

function closeChatbot() {
    document.getElementById('chatbotModal').classList.remove('open');
}

function minimizeChatbot() {
    closeChatbot();
}

// Show chatbot FAB when resume is uploaded
function showChatbotFab() {
    document.getElementById('chatbotBtn').classList.add('show');
}

// Add typing indicator
function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbotMessages');
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

// Get current time
function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

// Send chatbot message
async function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesContainer = document.getElementById('chatbotMessages');
    const sendButton = document.querySelector('.chatbot-send');
    
    // Remove welcome message if it exists
    const welcomeMsg = messagesContainer.querySelector('.chatbot-welcome');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chatbot-message user';
    userMsg.innerHTML = `${message}<span class="message-time">${getCurrentTime()}</span>`;
    messagesContainer.appendChild(userMsg);
    
    input.value = '';
    input.disabled = true;
    sendButton.disabled = true;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Show typing indicator
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

// Handle Enter key in chatbot input
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
            
            // Update profile with merged data
            if (data.unified_profile) {
                displayResumeData(data.unified_profile);
            }
            
            profileBuilt = true;
            
            // Hide LinkedIn section and show job recommendations
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
            
            // Hide LinkedIn section and show job recommendations
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

// Job Recommendations Functions
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
    
    // Display job recommendations
    data.recommendations.forEach((job, index) => {
        html += `
            <div class="job-card">
                <div class="job-header">
                    <h3>${job.job_title}</h3>
                    <div class="match-score" style="background: linear-gradient(135deg, #667eea ${job.match_score}%, #ddd ${job.match_score}%);">
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
    
    // Display career insights
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
