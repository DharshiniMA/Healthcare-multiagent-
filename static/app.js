const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'ai-message');
    
    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.textContent = sender === 'user' ? 'U' : 'AI';
    
    const textDiv = document.createElement('div');
    textDiv.classList.add('text');
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(textDiv);
    chatBox.appendChild(messageDiv);
    
    // Smooth scrolling
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return textDiv;
}

function showLoading() {
    const textDiv = appendMessage('ai', '');
    textDiv.classList.add('loading');
    textDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    return textDiv.parentElement;
}

async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // Clear input
    userInput.value = '';
    
    // Show user message
    appendMessage('user', query);
    
    // Show loading
    const loadingMsg = showLoading();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        const data = await response.json();
        
        // Remove loading
        loadingMsg.remove();
        
        if (response.ok) {
            appendMessage('ai', data.response);
        } else {
            appendMessage('ai', 'Sorry, I encountered an error: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        loadingMsg.remove();
        appendMessage('ai', 'Connection error. Please ensure the server is running and try again.');
    }
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
