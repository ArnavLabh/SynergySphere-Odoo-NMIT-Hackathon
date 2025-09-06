// Enhanced Error Handling and UX Feedback
class ErrorHandler {
    static showError(container, message, type = 'error') {
        this.clearErrors(container);
        const errorEl = document.createElement('div');
        errorEl.className = `message ${type}`;
        errorEl.setAttribute('role', 'alert');
        errorEl.setAttribute('aria-live', 'polite');
        errorEl.textContent = message;
        container.insertBefore(errorEl, container.firstChild);
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => errorEl.remove(), 5000);
        }
    }

    static showFieldErrors(form, fieldErrors) {
        Object.entries(fieldErrors).forEach(([field, message]) => {
            const input = form.querySelector(`[name="${field}"], #${field}`);
            if (input) {
                this.showFieldError(input, message);
            }
        });
    }

    static showFieldError(input, message) {
        this.clearFieldError(input);
        input.setAttribute('aria-invalid', 'true');
        input.classList.add('error');
        
        const errorEl = document.createElement('div');
        errorEl.className = 'field-error';
        errorEl.textContent = message;
        errorEl.id = `${input.id || input.name}-error`;
        input.setAttribute('aria-describedby', errorEl.id);
        
        input.parentNode.appendChild(errorEl);
    }

    static clearFieldError(input) {
        input.setAttribute('aria-invalid', 'false');
        input.classList.remove('error');
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) existingError.remove();
    }

    static clearErrors(container) {
        container.querySelectorAll('.message, .field-error').forEach(el => el.remove());
        container.querySelectorAll('[aria-invalid="true"]').forEach(input => {
            this.clearFieldError(input);
        });
    }

    static handleApiError(error, container, form = null) {
        if (error.field_errors && form) {
            this.showFieldErrors(form, error.field_errors);
            this.showError(container, error.error || 'Please fix the errors below');
        } else {
            const message = this.getErrorMessage(error);
            this.showError(container, message);
        }
    }

    static getErrorMessage(error) {
        if (typeof error === 'string') return error;
        if (error.error) return error.error;
        if (error.message) return error.message;
        return 'An unexpected error occurred';
    }

    static showLoading(button, text = 'Loading...') {
        button.disabled = true;
        button.dataset.originalText = button.textContent;
        button.textContent = text;
        button.classList.add('loading');
    }

    static hideLoading(button) {
        button.disabled = false;
        button.textContent = button.dataset.originalText || 'Submit';
        button.classList.remove('loading');
    }
}

// Enhanced API class with better error handling
class EnhancedAPI extends API {
    static async request(endpoint, options = {}) {
        try {
            const response = await super.request(endpoint, options);
            return response;
        } catch (error) {
            // Parse API error response
            if (error.message.startsWith('{')) {
                try {
                    const parsed = JSON.parse(error.message);
                    throw parsed;
                } catch (e) {
                    // If parsing fails, use original error
                }
            }
            throw error;
        }
    }
}

// Form validation utilities
class FormValidator {
    static validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    static validateRequired(value) {
        return value && value.trim().length > 0;
    }

    static validateMinLength(value, min) {
        return value && value.length >= min;
    }

    static validateForm(form, rules) {
        const errors = {};
        
        Object.entries(rules).forEach(([field, fieldRules]) => {
            const input = form.querySelector(`[name="${field}"], #${field}`);
            if (!input) return;
            
            const value = input.value;
            
            fieldRules.forEach(rule => {
                if (rule.type === 'required' && !this.validateRequired(value)) {
                    errors[field] = rule.message || `${field} is required`;
                } else if (rule.type === 'email' && value && !this.validateEmail(value)) {
                    errors[field] = rule.message || 'Please enter a valid email';
                } else if (rule.type === 'minLength' && value && !this.validateMinLength(value, rule.value)) {
                    errors[field] = rule.message || `Must be at least ${rule.value} characters`;
                } else if (rule.type === 'match' && value !== form.querySelector(rule.field).value) {
                    errors[field] = rule.message || 'Fields do not match';
                }
            });
        });
        
        return errors;
    }
}