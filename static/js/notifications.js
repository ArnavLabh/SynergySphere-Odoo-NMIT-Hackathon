// Notification System
class NotificationManager {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.loadNotifications();
    }

    createContainer() {
        // Create notification container if it doesn't exist
        this.container = document.getElementById('notificationContainer');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notificationContainer';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(this.container);
        }
    }

    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid var(--primary);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 0.5rem;
            color: var(--light);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(20px);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            position: relative;
        `;

        // Set border color based on type
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: 'var(--primary)'
        };
        notification.style.borderColor = colors[type] || colors.info;

        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="font-size: 1.2rem;">
                    ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}
                </div>
                <div style="flex: 1;">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; color: var(--light); cursor: pointer; font-size: 1.2rem;">×</button>
            </div>
        `;

        this.container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.style.transform = 'translateX(100%)';
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        }

        return notification;
    }

    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    }

    async loadNotifications() {
        // This would load notifications from the server
        // For now, we'll just show a welcome notification
        if (auth.isAuthenticated()) {
            setTimeout(() => {
                this.info(`Welcome back, ${auth.user?.name || 'User'}!`);
            }, 1000);
        }
    }

    // Show notification for task updates
    taskUpdated(taskTitle, newStatus) {
        const statusEmojis = {
            'todo': '📋',
            'in_progress': '⏳',
            'done': '✅'
        };
        const statusNames = {
            'todo': 'To Do',
            'in_progress': 'In Progress',
            'done': 'Done'
        };
        
        this.success(`${statusEmojis[newStatus]} Task "${taskTitle}" moved to ${statusNames[newStatus]}`);
    }

    // Show notification for new messages
    newMessage(projectName, senderName) {
        this.info(`💬 New message in "${projectName}" from ${senderName}`);
    }

    // Show notification for project events
    projectCreated(projectName) {
        this.success(`🚀 Project "${projectName}" created successfully!`);
    }

    memberAdded(memberName, projectName) {
        this.info(`👥 ${memberName} joined "${projectName}"`);
    }
}

// Initialize notification manager
const notifications = new NotificationManager();

// Make it globally available
window.notifications = notifications;