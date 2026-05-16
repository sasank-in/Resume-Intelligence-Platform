// Get session ID from URL parameter
const urlParams = new URLSearchParams(window.location.search);
let sessionId = urlParams.get('session') || localStorage.getItem('sessionId');
let profileBuilt = false;

if (!sessionId) {
    showLoadError({
        title: 'No session found',
        body: 'It looks like you opened this page without uploading a resume first.',
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    if (sessionId) await loadAnalysisData();
});

async function loadAnalysisData() {
    try {
        const response = await fetch('/get-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await response.json().catch(() => ({}));

        if (response.ok) {
            if (data.resume_data) displayResumeData(data.resume_data);
            if (data.analysis) displayAnalysis(data.analysis);
            document.getElementById('linkedinSection').style.display = 'block';
            showChatbotFab();
            return;
        }

        // Backend rejected — most likely an expired or unknown session.
        const expired = response.status === 400;
        showLoadError({
            title: expired ? 'Session expired' : 'We couldn\'t load your analysis',
            body: data.detail || 'Please try again or upload your resume again.',
            sessionLikelyDead: expired,
        });
    } catch (error) {
        console.error('Error loading analysis:', error);
        showLoadError({
            title: 'Network error',
            body: 'We couldn\'t reach the server. Check your connection and try again.',
            sessionLikelyDead: false,
        });
    }
}

/** Render an inline error card with Retry / Start Over actions. */
function showLoadError({ title, body, sessionLikelyDead }) {
    const host = document.querySelector('.content-container') || document.body;
    let card = document.getElementById('analysisLoadError');
    if (!card) {
        card = document.createElement('section');
        card.id = 'analysisLoadError';
        card.className = 'section';
        host.prepend(card);
    }
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    card.innerHTML = `
        <div class="upload-card" style="padding: 2rem; text-align: center;">
            <h2 class="section-title" style="text-align: center;">${esc(title)}</h2>
            <p class="section-description" style="margin: 0.5rem auto 1.25rem; max-width: 36rem;">${esc(body)}</p>
            <div style="display: inline-flex; gap: 0.75rem; flex-wrap: wrap; justify-content: center;">
                <button class="btn btn-secondary" id="retryAnalysisBtn">Retry</button>
                <a class="btn btn-primary" href="/">Start over</a>
            </div>
        </div>
    `;
    document.getElementById('retryAnalysisBtn').addEventListener('click', () => {
        if (sessionLikelyDead) {
            window.location.href = '/';
            return;
        }
        card.remove();
        loadAnalysisData();
    });
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
    
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));

    // Skills Section
    if (data.skills && data.skills.length > 0) {
        const skillsGrid = document.getElementById('skillsGrid');
        skillsGrid.innerHTML = data.skills.map(skill =>
            `<div class="skill-badge">${esc(skill)}</div>`
        ).join('');
        document.getElementById('skillsSection').style.display = 'block';
    }

    // Experience Timeline
    if (data.experience && data.experience.length > 0) {
        const timeline = document.getElementById('experienceTimeline');
        timeline.innerHTML = data.experience.map(exp => `
            <div class="timeline-item">
                <div class="timeline-date">${esc(exp.duration)}</div>
                <div class="timeline-content">
                    <h4>${esc(exp.title)}</h4>
                    <p class="company">${esc(exp.company)}</p>
                    ${exp.highlights && exp.highlights.length > 0 ? `
                        <ul class="highlights">
                            ${exp.highlights.map(h => `<li>${esc(h)}</li>`).join('')}
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
                <h4>${esc(edu.degree)}</h4>
                <p class="institution">${esc(edu.institution)}</p>
                <p class="year">${esc(edu.year)}</p>
                ${edu.details ? `<p class="details">${esc(edu.details)}</p>` : ''}
            </div>
        `).join('');
        document.getElementById('educationSection').style.display = 'block';
    }
}

function displayAnalysis(analysis) {
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    try {
        const analysisGrid = document.getElementById('analysisGrid');
        analysisGrid.innerHTML = '';

        function toText(val) {
            if (val == null) return '';
            if (Array.isArray(val)) return val.filter(Boolean).join(', ');
            if (typeof val === 'string') {
                const v = val.trim();
                if (v === '-' || v.includes('Analysis pending') || v.includes('unavailable')) return '';
                return v;
            }
            return String(val);
        }

        function combineDevAndCareerMoves(improvementAreas, nextCareerMoves) {
            const areas = toText(improvementAreas);
            const moves = toText(nextCareerMoves);
            if (!areas && !moves) return null;
            let combined = '';
            if (areas) {
                combined += `<div class="merged-section"><h4 class="merged-subtitle">🎯 Development Areas</h4><p>${esc(areas)}</p></div>`;
            }
            if (moves) {
                if (combined) combined += '<div class="section-divider"></div>';
                combined += `<div class="merged-section"><h4 class="merged-subtitle">🚀 Next Career Moves</h4><p>${esc(moves)}</p></div>`;
            }
            return combined || null;
        }

        const analysisCards = [
            { key: 'overall_score', icon: '⭐', title: 'Overall Assessment', value: toText(analysis.overall_score), type: 'score' },
            { key: 'career_trajectory', icon: '📈', title: 'Career Trajectory', value: toText(analysis.career_trajectory) },
            { key: 'key_strengths', icon: '💪', title: 'Core Strengths', value: toText(analysis.key_strengths) },
            {
                key: 'development_and_career_moves',
                icon: '🎯',
                title: 'Development Areas & Next Career Moves',
                value: combineDevAndCareerMoves(analysis.improvement_areas, analysis.next_career_moves),
                fullWidth: true,
                rawHtml: true,  // already-safe, escape-built HTML
            },
            { key: 'industry_fit', icon: '🏢', title: 'Best Fit Industries', value: toText(analysis.industry_fit) },
            { key: 'competitive_advantage', icon: '🚀', title: 'Competitive Advantage', value: toText(analysis.competitive_advantage) },
            { key: 'salary_expectations', icon: '💰', title: 'Salary Insights', value: toText(analysis.salary_expectations) },
            { key: 'recommendations_summary', icon: '💡', title: 'Comprehensive Recommendations', value: toText(analysis.recommendations_summary), fullWidth: true },
        ];

        analysisCards.forEach(card => {
            if (!card.value) return;
            const cardElement = document.createElement('div');
            cardElement.className = `analysis-card ${card.fullWidth ? 'full-width' : ''}`;

            let contentHTML;
            if (card.type === 'score') {
                contentHTML = `<div class="analysis-score-badge">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                    </svg>${esc(card.value)}</div>`;
            } else if (card.rawHtml) {
                contentHTML = card.value;
            } else {
                contentHTML = `<p>${esc(card.value)}</p>`;
            }

            cardElement.innerHTML = `
                <div class="analysis-card-header">
                    <div class="analysis-icon">${card.icon}</div>
                    <h3>${esc(card.title)}</h3>
                </div>
                <div class="analysis-card-content">${contentHTML}</div>
            `;
            analysisGrid.appendChild(cardElement);
        });

        const analysisSection = document.getElementById('analysisSection');
        if (analysisGrid.children.length > 0) {
            analysisSection.style.display = 'block';
        } else {
            // Empty fallback so the user isn't staring at a blank page.
            analysisGrid.innerHTML = `
                <div class="empty-state full-width">
                    <h3>Analysis is light on details</h3>
                    <p>Our AI couldn't generate confident insights from this resume.
                       Try uploading a more detailed PDF — work history with dates, accomplishments,
                       and a skills section produces the best results.</p>
                    <div class="empty-state-actions">
                        <a class="btn btn-secondary" href="/">Upload a different resume</a>
                    </div>
                </div>`;
            analysisSection.style.display = 'block';
        }

        // Professional Summary
        const suggestedJob = toText(analysis.suggested_job_summary);
        const suggestedJobSection = document.getElementById('suggestedJobSection');
        const suggestedJobSummaryEl = document.getElementById('suggestedJobSummary');

        if (suggestedJob) {
            suggestedJobSummaryEl.textContent = suggestedJob;
            suggestedJobSection.style.display = 'block';
        }
    } catch (error) {
        console.error('displayAnalysis failed:', error);
        // Surface a visible error rather than a silent blank page.
        const grid = document.getElementById('analysisGrid');
        if (grid) {
            grid.innerHTML = `
                <div class="empty-state full-width">
                    <h3>Couldn't render analysis</h3>
                    <p>Something went wrong displaying your results. Refresh to try again.</p>
                </div>`;
            document.getElementById('analysisSection').style.display = 'block';
        }
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

/** Safely append a chat bubble. Uses textContent so LLM/user text can never inject HTML. */
function appendChatBubble(container, kind, text) {
    const bubble = document.createElement('div');
    bubble.className = 'chatbot-message ' + kind;
    const body = document.createElement('span');
    body.className = 'message-body';
    body.textContent = text;  // text-only; newlines preserved by white-space: pre-wrap in CSS
    body.style.whiteSpace = 'pre-wrap';
    const time = document.createElement('span');
    time.className = 'message-time';
    time.textContent = getCurrentTime();
    bubble.appendChild(body);
    bubble.appendChild(time);
    container.appendChild(bubble);
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
    
    appendChatBubble(messagesContainer, 'user', message);

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
            appendChatBubble(messagesContainer, 'ai', data.response || '');
        } else {
            appendChatBubble(messagesContainer, 'ai error',
                '⚠️ ' + (data.detail || 'Could not get response'));
        }
    } catch (error) {
        hideTypingIndicator();
        appendChatBubble(messagesContainer, 'ai error', '⚠️ Error connecting to server');
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

// LinkedIn tab switching (paste vs URL)
document.addEventListener('click', (e) => {
    const tab = e.target.closest('.linkedin-tab');
    if (!tab) return;
    const paneId = tab.getAttribute('data-pane');
    if (!paneId) return;
    const tabs = tab.parentElement.querySelectorAll('.linkedin-tab');
    tabs.forEach(t => {
        const active = t === tab;
        t.classList.toggle('is-active', active);
        t.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    const linkedinSection = document.getElementById('linkedinSection');
    if (!linkedinSection) return;
    linkedinSection.querySelectorAll('.linkedin-pane').forEach(p => {
        p.classList.toggle('is-active', p.id === paneId);
    });
});

async function pasteLinkedInProfile() {
    const textEl = document.getElementById('linkedinText');
    const text = (textEl && textEl.value || '').trim();
    if (text.length < 40) {
        setLinkedInStatus('Paste at least the headline, experience, and skills sections.', 'error');
        if (window.UI) UI.toast('Need more LinkedIn text to merge', { type: 'info' });
        return;
    }
    setLinkedInStatus('Extracting fields from pasted text…', 'info');
    try {
        const response = await fetch('/paste-linkedin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ linkedin_text: text, session_id: sessionId })
        });
        const data = await response.json();
        if (response.ok) {
            setLinkedInStatus('LinkedIn data merged', 'success');
            if (window.UI) UI.toast('LinkedIn profile merged', { type: 'success' });
            if (data.unified_profile) displayResumeData(data.unified_profile);
            profileBuilt = true;
            setTimeout(() => {
                document.getElementById('linkedinSection').style.display = 'none';
                document.getElementById('jobRecommendationsSection').style.display = 'block';
            }, 1200);
        } else {
            const msg = data.detail || 'Could not merge LinkedIn text';
            setLinkedInStatus(msg, 'error');
            if (window.UI) UI.toast(msg, { type: 'error' });
        }
    } catch (error) {
        console.error('Paste LinkedIn error:', error);
        setLinkedInStatus('Network error — please try again', 'error');
        if (window.UI) UI.toast('LinkedIn merge failed', { type: 'error' });
    }
}

// LinkedIn Profile Functions
function setLinkedInStatus(message, kind) {
    // kind: 'info' | 'success' | 'error'
    const statusEl = document.getElementById('linkedinStatus');
    if (!statusEl) return;
    statusEl.textContent = message;
    statusEl.classList.remove('success', 'error');
    statusEl.classList.add('status-message');
    if (kind === 'success') statusEl.classList.add('success');
    else if (kind === 'error') statusEl.classList.add('error');
}

async function addLinkedInProfile() {
    const linkedinUrl = document.getElementById('linkedinUrl').value.trim();

    if (!linkedinUrl) {
        setLinkedInStatus('Please enter a LinkedIn profile URL', 'error');
        if (window.UI) UI.toast('Please enter a LinkedIn URL', { type: 'info' });
        return;
    }

    // Strict LinkedIn URL check: must be on linkedin.com domain
    let parsed;
    try { parsed = new URL(linkedinUrl); } catch {
        setLinkedInStatus('That doesn\'t look like a valid URL', 'error');
        return;
    }
    if (!/(^|\.)linkedin\.com$/i.test(parsed.hostname)) {
        setLinkedInStatus('URL must be on linkedin.com', 'error');
        return;
    }

    setLinkedInStatus('Extracting LinkedIn profile…', 'info');

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
            setLinkedInStatus('LinkedIn profile added successfully', 'success');
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
            const msg = data.detail || 'Failed to extract LinkedIn profile';
            setLinkedInStatus(msg, 'error');
            if (window.UI) UI.toast(msg, { type: 'error' });
        }
    } catch (error) {
        console.error('LinkedIn error:', error);
        setLinkedInStatus('Network error — try again or click Skip', 'error');
        if (window.UI) UI.toast('LinkedIn extraction failed', { type: 'error' });
    }
}

async function skipLinkedIn() {
    setLinkedInStatus('Building profile from resume only…', 'info');

    try {
        const response = await fetch('/skip-linkedin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        const data = await response.json();

        if (response.ok) {
            setLinkedInStatus('Profile created from resume', 'success');
            if (window.UI) UI.toast('Profile ready', { type: 'success' });

            profileBuilt = true;

            setTimeout(() => {
                document.getElementById('linkedinSection').style.display = 'none';
                document.getElementById('jobRecommendationsSection').style.display = 'block';
            }, 1000);
        } else {
            const msg = data.detail || 'Failed to build profile';
            setLinkedInStatus(msg, 'error');
            if (window.UI) UI.toast(msg, { type: 'error' });
        }
    } catch (error) {
        console.error('Skip LinkedIn error:', error);
        setLinkedInStatus('Network error — please try again', 'error');
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
    
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    if (!data || !Array.isArray(data.recommendations) || data.recommendations.length === 0) {
        contentEl.innerHTML = `
            <div class="empty-state">
                <h3>No recommendations yet</h3>
                <p>Try adding more details to your resume or LinkedIn — we couldn't find strong matches.</p>
            </div>`;
        return;
    }

    let html = '<div class="job-recommendations-grid">';

    data.recommendations.forEach(job => {
        const matching = Array.isArray(job.matching_skills) ? job.matching_skills : [];
        const gaps = Array.isArray(job.skill_gaps) ? job.skill_gaps : [];
        const score = Number(job.match_score) || 0;
        html += `
            <div class="job-card">
                <div class="job-header">
                    <h3>${esc(job.job_title || 'Untitled role')}</h3>
                    <div class="match-score" style="background: linear-gradient(135deg, #4f46e5 ${score}%, #ddd ${score}%);">
                        ${esc(score)}% Match
                    </div>
                </div>
                ${job.company_type ? `<p class="company-type">🏢 ${esc(job.company_type)}</p>` : ''}
                ${job.reasoning ? `<p class="job-reasoning">${esc(job.reasoning)}</p>` : ''}

                <div class="job-details">
                    ${matching.length > 0 ? `
                        <div class="job-section">
                            <h4>✅ Matching Skills</h4>
                            <div class="skills-tags">
                                ${matching.map(s => `<span class="skill-tag match">${esc(s)}</span>`).join('')}
                            </div>
                        </div>` : ''}

                    ${gaps.length > 0 ? `
                        <div class="job-section">
                            <h4>📚 Skills to Develop</h4>
                            <div class="skills-tags">
                                ${gaps.map(s => `<span class="skill-tag gap">${esc(s)}</span>`).join('')}
                            </div>
                        </div>` : ''}

                    <div class="job-footer">
                        ${job.salary_range ? `<span class="salary">💰 ${esc(job.salary_range)}</span>` : ''}
                        ${job.growth_potential ? `<span class="growth">📈 ${esc(job.growth_potential)}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';

    if (data.career_insights) {
        const ci = data.career_insights;
        const industries = Array.isArray(ci.recommended_industries) ? ci.recommended_industries : [];
        const nextRoles = Array.isArray(ci.next_level_roles) ? ci.next_level_roles : [];
        const priority = Array.isArray(ci.skill_development_priority) ? ci.skill_development_priority : [];
        html += `
            <div class="career-insights">
                <h3>💡 Career Insights</h3>
                <div class="insights-grid">
                    ${ci.strongest_areas ? `
                        <div class="insight-card">
                            <h4>🌟 Strongest Areas</h4>
                            <p>${esc(ci.strongest_areas)}</p>
                        </div>` : ''}
                    ${industries.length > 0 ? `
                        <div class="insight-card">
                            <h4>🏭 Recommended Industries</h4>
                            <div class="industry-tags">
                                ${industries.map(i => `<span class="industry-tag">${esc(i)}</span>`).join('')}
                            </div>
                        </div>` : ''}
                    ${nextRoles.length > 0 ? `
                        <div class="insight-card">
                            <h4>🚀 Next Level Roles</h4>
                            <ul>${nextRoles.map(r => `<li>${esc(r)}</li>`).join('')}</ul>
                        </div>` : ''}
                    ${priority.length > 0 ? `
                        <div class="insight-card">
                            <h4>📖 Priority Skills to Learn</h4>
                            <ul>${priority.map(s => `<li>${esc(s)}</li>`).join('')}</ul>
                        </div>` : ''}
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
    const esc = (window.UI && window.UI.escape) || (s => String(s == null ? '' : s));
    const score = Number(analysis.overall_score) || 0;
    const kw = analysis.keyword_analysis || {};
    const fmt = analysis.format_analysis || {};
    const struct = analysis.structure_analysis || {};
    const comp = analysis.competitive_analysis || {};
    const pass = analysis.pass_probability || {};
    const recs = Array.isArray(analysis.recommendations) ? analysis.recommendations : [];
    const matchedSkills = (Array.isArray(kw.required_skill_matches) ? kw.required_skill_matches : []).slice(0, 5);
    const missingSkills = (Array.isArray(kw.missing_required_skills) ? kw.missing_required_skills : []).slice(0, 5);
    const fmtIssues = (Array.isArray(fmt.issues) ? fmt.issues : []).slice(0, 3);
    const sections = Array.isArray(struct.section_order) ? struct.section_order : [];
    const num = (v, suf = '%') => (typeof v === 'number') ? v.toFixed(1) + suf : '—';

    resultsDiv.innerHTML = `
        <div class="ats-score-card">
            <div class="ats-score-value">${esc(score)}%</div>
            <div class="ats-score-label">ATS Compatibility Score</div>
            <div class="ats-score-description">${esc(pass.message || '')}</div>
        </div>

        <div class="ats-analysis-grid">
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
                    <div class="ats-score-fill ${getScoreClass(kw.keyword_score || 0)}"
                         style="width: ${Number(kw.keyword_score) || 0}%"></div>
                </div>
                <p><strong>Required Skills Match:</strong> ${num(kw.required_skill_coverage)}</p>
                <p><strong>Matching Skills:</strong> ${esc(matchedSkills.join(', ') || 'None')}</p>
                ${missingSkills.length > 0 ? `<p><strong>Missing:</strong> ${esc(missingSkills.join(', '))}</p>` : ''}
            </div>

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
                    <div class="ats-score-fill ${getScoreClass(fmt.format_score || 0)}"
                         style="width: ${Number(fmt.format_score) || 0}%"></div>
                </div>
                <p><strong>ATS-Friendly Elements:</strong> ${esc(Array.isArray(fmt.ats_friendly_elements) ? fmt.ats_friendly_elements.length : 0)}</p>
                ${fmtIssues.length > 0
                    ? `<p><strong>Issues:</strong> ${esc(fmtIssues.join(', '))}</p>`
                    : '<p><strong>Status:</strong> No major format issues detected</p>'}
            </div>

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
                    <div class="ats-score-fill ${getScoreClass(struct.structure_score || 0)}"
                         style="width: ${Number(struct.structure_score) || 0}%"></div>
                </div>
                <p><strong>Section Order:</strong> ${esc(sections.join(' → ') || '—')}</p>
                <p><strong>Consistency:</strong> ${num(struct.consistency_score)}</p>
            </div>
        </div>

        <div class="ats-analysis-card competitive-card">
            <div class="ats-analysis-header">
                <div class="ats-analysis-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                    </svg>
                </div>
                <div class="ats-analysis-title">Competitive Position</div>
            </div>
            <p><strong>Your Position:</strong> ${esc(comp.percentile || '—')} of candidates</p>
            <p><strong>Pass Probability:</strong> ${esc(pass.probability || '—')}</p>
            <p><strong>Industry Benchmark:</strong> ${esc(comp.benchmark_score ?? '—')}%</p>
        </div>

        <div class="ats-recommendations">
            <h4>Improvement Recommendations</h4>
            ${recs.length > 0
                ? recs.map(rec => `
                    <div class="recommendation-item">
                        <div class="recommendation-header">
                            <span class="priority-badge ${esc((rec.priority || '').toLowerCase())}">${esc(rec.priority || '')}</span>
                            <span class="recommendation-category">${esc(rec.category || '')}</span>
                        </div>
                        <div class="recommendation-issue">${esc(rec.issue || '')}</div>
                        <div class="recommendation-action">${esc(rec.action || '')}</div>
                        <div class="recommendation-impact">Impact: ${esc(rec.impact || '')}</div>
                    </div>
                `).join('')
                : '<p class="hint">No specific recommendations.</p>'}
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