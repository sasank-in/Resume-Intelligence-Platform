let sessionId = Date.now().toString();

document.getElementById('pdfFile').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    document.getElementById('fileName').textContent = `Selected: ${file.name}`;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('status').textContent = '';
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        const statusEl = document.getElementById('status');
        
        if (response.ok) {
            document.getElementById('summary').textContent = data.summary;
            document.getElementById('summaryBox').style.display = 'block';
            document.getElementById('qaSection').style.display = 'block';
            statusEl.textContent = 'PDF processed successfully';
            statusEl.className = 'status success';
            statusEl.style.display = 'block';
        } else {
            statusEl.textContent = 'Error: ' + data.detail;
            statusEl.className = 'status error';
            statusEl.style.display = 'block';
        }
    } catch (error) {
        document.getElementById('status').textContent = '❌ Error uploading file';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});

async function askQuestion() {
    const question = document.getElementById('questionInput').value.trim();
    if (!question) return;
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('answerBox').style.display = 'none';
    
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('answer').textContent = data.answer;
            
            // Display sources if available
            if (data.sources && data.sources.length > 0) {
                const sourcesList = document.getElementById('sourcesList');
                sourcesList.innerHTML = data.sources.map(source => 
                    `<div class="source-item">
                        <span class="source-page">Page ${source.page}:</span> 
                        ${source.content}...
                    </div>`
                ).join('');
                document.getElementById('sources').style.display = 'block';
            }
            
            document.getElementById('answerBox').style.display = 'block';
        } else {
            alert('Error: ' + data.detail);
        }
    } catch (error) {
        alert('Error asking question');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

document.getElementById('questionInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') askQuestion();
});
