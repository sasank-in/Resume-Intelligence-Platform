let sessionId = Date.now().toString();

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
}

// Chatbot modal functionality
function toggleChatbot() {
    const modal = document.getElementById('chatbotModal');
    modal.classList.toggle('open');
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

// Send chatbot message
async function sendChatbotMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesContainer = document.getElementById('chatbotMessages');
    
    // Add user message
    const userMsg = document.createElement('div');
    userMsg.className = 'chatbot-message user';
    userMsg.textContent = message;
    messagesContainer.appendChild(userMsg);
    
    input.value = '';
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const aiMsg = document.createElement('div');
            aiMsg.className = 'chatbot-message ai';
            aiMsg.textContent = data.response;
            messagesContainer.appendChild(aiMsg);
        } else {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chatbot-message ai error';
            errorMsg.textContent = 'Error: ' + (data.detail || 'Could not get response');
            messagesContainer.appendChild(errorMsg);
        }
    } catch (error) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'chatbot-message ai error';
        errorMsg.textContent = 'Error connecting to server';
        messagesContainer.appendChild(errorMsg);
    }
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
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

