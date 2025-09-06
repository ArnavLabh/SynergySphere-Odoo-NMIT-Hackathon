// Accessibility utilities and enhancements
class AccessibilityManager {
    static init() {
        this.setupKeyboardNavigation();
        this.setupAriaUpdates();
        this.setupFocusManagement();
        this.announcePageChanges();
    }

    static setupKeyboardNavigation() {
        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal[style*="flex"]');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });

        // Tab navigation for hamburger menu
        const hamburger = document.getElementById('hamburger');
        const navLinks = document.getElementById('navLinks');
        
        if (hamburger) {
            hamburger.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleMobileMenu();
                }
            });
        }
    }

    static setupAriaUpdates() {
        // Update ARIA attributes dynamically
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('invalid', () => {
                    input.setAttribute('aria-invalid', 'true');
                });
                
                input.addEventListener('input', () => {
                    if (input.validity.valid) {
                        input.setAttribute('aria-invalid', 'false');
                    }
                });
            });
        });
    }

    static setupFocusManagement() {
        // Focus management for modals
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'style') {
                        const isVisible = modal.style.display === 'flex';
                        if (isVisible) {
                            this.trapFocus(modal);
                            modal.setAttribute('aria-hidden', 'false');
                        } else {
                            modal.setAttribute('aria-hidden', 'true');
                        }
                    }
                });
            });
            observer.observe(modal, { attributes: true });
        });
    }

    static trapFocus(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // Focus first element
        setTimeout(() => firstElement?.focus(), 100);

        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement?.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement?.focus();
                    }
                }
            }
        });
    }

    static toggleMobileMenu() {
        const hamburger = document.getElementById('hamburger');
        const navLinks = document.getElementById('navLinks');
        
        if (hamburger && navLinks) {
            const isExpanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !isExpanded);
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        }
    }

    static closeModal(modal) {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        
        // Return focus to trigger element
        const trigger = document.querySelector(`[onclick*="${modal.id}"]`);
        trigger?.focus();
    }

    static announcePageChanges() {
        // Create live region for dynamic content updates
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'visually-hidden';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);
    }

    static announce(message) {
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => liveRegion.textContent = '', 1000);
        }
    }

    static updateTaskStatus(taskElement, newStatus) {
        // Announce task status changes
        const taskTitle = taskElement.querySelector('h4')?.textContent;
        this.announce(`Task "${taskTitle}" moved to ${newStatus}`);
    }

    static updateFormErrors(form, errors) {
        const errorContainer = form.querySelector('[role="alert"]');
        if (errorContainer && errors.length > 0) {
            errorContainer.textContent = errors.join('. ');
            errorContainer.style.display = 'block';
            
            // Mark invalid fields
            errors.forEach(error => {
                const field = form.querySelector(`[name="${error.field}"]`);
                if (field) {
                    field.setAttribute('aria-invalid', 'true');
                }
            });
        }
    }
}

// Initialize accessibility features when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AccessibilityManager.init();
});

// Export for use in other modules
window.AccessibilityManager = AccessibilityManager;