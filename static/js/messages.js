// Messages Management
class Messages {
    constructor() {
        this.messages = [];
        this.currentProjectId = null;
        this.pollInterval = null;
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const messageForm = document.getElementById('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', this.handleSendMessage.bind(this));
        }
    }

    async loadMessages(projectId) {
        this.currentProjectId = projectId;
        
        try {
            const response = await API.get(`/projects/${projectId}/messages`);
            this.messages = response.messages || [];
            this.renderMessages();
            this.startPolling();
        } catch (error) {
            console.error('Failed to load messages:', error);
            this.messages = [];
            this.renderMessages();
        }
    }

    renderMessages() {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;

        if (this.messages.length === 0) {
            messagesList.innerHTML = `
                <div class="empty-messages">
                    <div class="empty-icon">💬</div>
                    <h3>No messages yet</h3>
                    <p>Start the conversation by sending the first message</p>
                </div>
            `;
            return;
        }

        messagesList.innerHTML = this.messages.map(message => `
            <div class="message ${message.user_id === auth.user.id ? 'own-message' : ''}">
                <div class="message-header">
                    <span class="message-author">${message.user_name || 'Unknown User'}</span>
                    <span class="message-time">${this.formatTime(message.created_at)}</span>
                </div>
                <div class="message-content">${this.escapeHtml(message.content)}</div>
            </div>
        `).join('');

        // Scroll to bottom
        messagesList.scrollTop = messagesList.scrollHeight;
    }

    async handleSendMessage(e) {
        e.preventDefault();
        
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        try {
            await API.post(`/projects/${this.currentProjectId}/messages`, { content: message });
            messageInput.value = '';
            this.loadMessages(this.currentProjectId);
            
            // Show success notification
            if (window.notifications) {
                window.notifications.success('Message sent!');
            }
        } catch (error) {
            const errorMsg = error.message || 'Failed to send message';
            this.showError(errorMsg);
            if (window.notifications) {
                window.notifications.error(errorMsg);
            }
        }
    }

    startPolling() {
        // Clear existing polling
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        // Poll for new messages every 10 seconds
        this.pollInterval = setInterval(() => {
            if (this.currentProjectId) {
                this.loadMessages(this.currentProjectId);
            }
        }, 10000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);

        if (diffInHours < 1) {
            const diffInMinutes = Math.floor((now - date) / (1000 * 60));
            return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes}m ago`;
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        if (window.notifications) {
            window.notifications.error(message);
        } else {
            alert(message);
        }
    }
}

// Initialize messages
const messages = new Messages();
messages.init();

// Stop polling when leaving the page
window.addEventListener('beforeunload', () => {
    messages.stopPolling();
});