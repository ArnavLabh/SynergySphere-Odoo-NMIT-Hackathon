// API communication functions
const API_BASE = '/api';

// Enhanced logging for frontend
class Logger {
    static log(level, message, context = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            level: level.toUpperCase(),
            message,
            url: window.location.href,
            userAgent: navigator.userAgent,
            ...context
        };
        
        console[level](JSON.stringify(logEntry));
        
        // Send critical errors to backend
        if (level === 'error') {
            fetch('/api/client-errors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logEntry)
            }).catch(() => {}); // Fail silently
        }
    }
    
    static info(message, context) { this.log('info', message, context); }
    static warn(message, context) { this.log('warn', message, context); }
    static error(message, context) { this.log('error', message, context); }
}

// API utility functions
class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const requestId = Math.random().toString(36).substr(2, 9);
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'X-Request-ID': requestId,
                ...auth.getAuthHeaders(),
                ...options.headers
            },
            ...options
        };

        Logger.info(`API Request: ${options.method || 'GET'} ${endpoint}`, { requestId });

        try {
            const response = await fetch(url, config);
            
            if (response.status === 204) {
                Logger.info(`API Response: ${response.status} (empty)`, { requestId, endpoint });
                return null;
            }
            
            const data = await response.json();
            
            if (!response.ok) {
                Logger.error(`API Error ${response.status}`, { 
                    requestId, endpoint, error: data, status: response.status 
                });
                throw data;
            }
            
            Logger.info(`API Success: ${response.status}`, { requestId, endpoint });
            return data;
        } catch (error) {
            Logger.error('API Request Failed', { 
                requestId, endpoint, error: error.message, stack: error.stack 
            });
            throw error;
        }
    }

    static async get(endpoint) {
        return this.request(endpoint);
    }

    static async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    static async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }

    static async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
}