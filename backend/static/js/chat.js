// Chat functionality
let sessionId = null;
let isLoading = false;

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');

// Start session on page load
async function startSession() {
    try {
        const response = await fetch('/api/chat/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: '{}'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        sessionId = data.id;  // Changed from data.session_id
        
        // Get the last message from the messages array
        if (data.messages && data.messages.length > 0) {
            const lastMessage = data.messages[data.messages.length - 1];
            addMessage('assistant', lastMessage.content);
        }
    } catch (error) {
        console.error('Failed to start session:', error);
        addMessage('assistant', 'Sorry, something went wrong. Please refresh the page.');
    }
}

// Add message to chat
function addMessage(role, content, isWarning = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}${isWarning ? ' warning' : ''}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function hideTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) {
        typing.remove();
    }
}

// Send message
async function sendMessage() {
    if (!chatInput.value.trim() || !sessionId || isLoading) return;
    
    const message = chatInput.value.trim();
    chatInput.value = '';
    
    addMessage('user', message);
    isLoading = true;
    sendBtn.disabled = true;
    showTyping();
    
    try {
        const response = await fetch('/api/chat/continue', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: message
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API Response:', data);  // Debug log
        hideTyping();
        
        // Show trigger warning if present
        if (data.trigger_warning) {
            addMessage('assistant', data.trigger_warning, true);
        }
        
        // Show main message
        if (data.message) {
            addMessage('assistant', data.message);
        }
        
        // Handle triage completion
        if (data.should_triage && data.triage_result === 'clinic') {
            showBookingOptions();
        } else if (data.should_triage && data.triage_result === 'emergency') {
            // Emergency - no booking options
            sendBtn.disabled = true;
            chatInput.disabled = true;
        }
        
    } catch (error) {
        console.error('Failed to send message:', error);
        hideTyping();
        addMessage('assistant', 'Sorry, something went wrong. Please try again.');
    } finally {
        isLoading = false;
        sendBtn.disabled = false;
    }
}

// Show booking options
function showBookingOptions() {
    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'booking-options-container';
    optionsDiv.innerHTML = `
        <h3>How would you like to proceed?</h3>
        <p class="booking-options-subtitle">Choose your preferred booking method</p>
        
        <div class="booking-choice-cards">
            <div class="booking-choice-card" onclick="window.location.href='/clinics?booking=direct'">
                <div class="choice-icon">📅</div>
                <h4>Book Appointment Directly</h4>
                <p>Quick booking - Select clinic, date, and time</p>
                <button class="btn btn-primary btn-block">Book Now</button>
            </div>

            <div class="booking-choice-card" onclick="window.location.href='/clinics?booking=ai'">
                <div class="choice-icon">💬</div>
                <h4>Book with AI Assistant</h4>
                <p>Select clinic and chat with their AI assistant</p>
                <button class="btn btn-secondary btn-block">Choose Clinic</button>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(optionsDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Disable input
    chatInput.disabled = true;
    sendBtn.disabled = true;
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize
startSession();
