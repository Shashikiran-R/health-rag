document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');
    const typingIndicator = document.getElementById('typing-indicator');

    // Configure marked for Markdown parsing
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.textContent = isUser ? 'U' : 'AI';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        if (isUser) {
            contentDiv.textContent = content; // Escape user input
        } else {
            contentDiv.innerHTML = marked.parse(content); // Render AI markdown
        }

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        // Insert before typing indicator
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function setTyping(isTyping) {
        if (isTyping) {
            typingIndicator.classList.remove('hidden');
            sendButton.disabled = true;
            userInput.disabled = true;
        } else {
            typingIndicator.classList.add('hidden');
            sendButton.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
        scrollToBottom();
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const query = userInput.value.trim();
        if (!query) return;

        // Display user message
        addMessage(query, true);
        userInput.value = '';
        
        // Show typing indicator
        setTyping(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            setTyping(false);
            addMessage(data.response, false);

        } catch (error) {
            console.error('Error:', error);
            setTyping(false);
            addMessage('⚠️ Sorry, there was an error processing your request. Please try again.', false);
        }
    });
});
