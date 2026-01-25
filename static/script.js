let sessionId = Date.now().toString();

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    const resumeFileInput = document.getElementById('resumeFile');
    
    if (!resumeFileInput) {
        console.error('Resume file input not found!');
        return;
    }
    
    resumeFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const fileNameEl = document.getElementById('fileName');
        const loadingEl = document.getElementById('loading');
        const statusEl = document.getElementById('status');
        
        // Verify all elements exist
        if (!fileNameEl) console.warn('fileName element not found');
        if (!loadingEl) console.warn('loading element not found');
        if (!statusEl) console.warn('status element not found');
        
        if (fileNameEl) {
            fileNameEl.textContent = `Selected: ${file.name}`;
        }
        
        if (loadingEl) {
            loadingEl.style.display = 'block';
        }
        
        if (statusEl) {
            statusEl.textContent = '';
            statusEl.style.display = 'none';
        }
        
        // Animate loading steps
        animateLoadingSteps();
        
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
            console.log('Upload response ok:', response.ok);
            
            const data = await response.json();
            console.log('Upload response data:', JSON.stringify(data, null, 2));
            
            if (response.ok) {
                console.log('Upload successful! Preparing to redirect...');
                
                // Clear loading animation interval immediately
                if (window.loadingInterval) {
                    clearInterval(window.loadingInterval);
                    console.log('Loading interval cleared');
                }
                if (loadingEl) {
                    loadingEl.style.display = 'none';
                    console.log('Loading overlay hidden');
                }
                
                if (statusEl) {
                    statusEl.textContent = '✓ Resume analyzed successfully! Redirecting...';
                    statusEl.className = 'alert success';
                    statusEl.style.display = 'block';
                }
                
                // Store session ID in localStorage
                localStorage.setItem('sessionId', sessionId);
                console.log('Session ID stored:', sessionId);
                
                // Redirect to analysis page after a short delay
                const redirectUrl = `/analysis.html?session=${sessionId}`;
                console.log('Will redirect to:', redirectUrl);
                
                // Set up redirect with fallback
                const redirectTimer = setTimeout(() => {
                    console.log('Redirecting now...');
                    try {
                        window.location.href = redirectUrl;
                    } catch (redirectError) {
                        console.error('Redirect error:', redirectError);
                        // Fallback: try assign instead
                        window.location.assign(redirectUrl);
                    }
                }, 1500);
                
                // Also add a manual redirect button as backup
                if (statusEl) {
                    const redirectBtn = document.createElement('button');
                    redirectBtn.className = 'btn btn-primary';
                    redirectBtn.textContent = 'View Analysis';
                    redirectBtn.style.marginTop = '10px';
                    redirectBtn.onclick = () => {
                        clearTimeout(redirectTimer);
                        window.location.href = redirectUrl;
                    };
                    statusEl.appendChild(document.createElement('br'));
                    statusEl.appendChild(redirectBtn);
                }
            } else {
                console.error('Upload failed with status:', response.status);
                if (statusEl) {
                    statusEl.textContent = 'Error: ' + (data.detail || 'Failed to upload resume');
                    statusEl.className = 'alert error';
                    statusEl.style.display = 'block';
                }
                console.error('Upload error:', data);
            }
        } catch (error) {
            console.error('Upload error details:', error);
            console.error('Error stack:', error.stack);
            if (statusEl) {
                let errorMessage = '❌ Error uploading resume. ';
                
                // Provide specific error messages
                if (error.message.includes('413') || error.message.includes('too large')) {
                    errorMessage += 'File is too large. Please use a PDF under 10MB.';
                } else if (error.message.includes('400') || error.message.includes('PDF')) {
                    errorMessage += 'Please upload a valid PDF file with selectable text.';
                } else if (error.message.includes('network') || error.message.includes('fetch')) {
                    errorMessage += 'Network error. Please check your connection and try again.';
                } else {
                    errorMessage += 'Please try again or contact support if the issue persists.';
                }
                
                statusEl.textContent = errorMessage;
                statusEl.className = 'alert error';
                statusEl.style.display = 'block';
            }
        } finally {
            console.log('Upload process completed, cleaning up...');
            // Clear loading animation interval
            if (window.loadingInterval) {
                clearInterval(window.loadingInterval);
                console.log('Loading interval cleared');
            }
            if (loadingEl) {
                loadingEl.style.display = 'none';
                console.log('Loading overlay hidden');
            }
        }
    });
});

// Animate loading steps
function animateLoadingSteps() {
    const steps = ['step1', 'step2', 'step3'];
    let currentStep = 0;
    
    const interval = setInterval(() => {
        if (currentStep > 0) {
            const prevStep = document.getElementById(steps[currentStep - 1]);
            if (prevStep) {
                prevStep.classList.remove('active');
                prevStep.classList.add('completed');
                const icon = prevStep.querySelector('.step-icon');
                if (icon) icon.textContent = '✓';
            }
        }
        
        if (currentStep < steps.length) {
            const step = document.getElementById(steps[currentStep]);
            if (step) {
                step.classList.add('active');
            }
            currentStep++;
        } else {
            clearInterval(interval);
        }
    }, 800);
    
    // Store interval ID to clear it when loading completes
    window.loadingInterval = interval;
}
