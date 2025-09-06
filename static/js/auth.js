// Authentication Management
class Auth {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.init();
    }

    init() {
        if (document.getElementById('loginForm')) {
            document.getElementById('loginForm').addEventListener('submit', this.handleLogin.bind(this));
        }
        if (document.getElementById('registerForm')) {
            document.getElementById('registerForm').addEventListener('submit', this.handleRegister.bind(this));
        }
        this.updateNavigation();
    }

    async handleLogin(e) {
        e.preventDefault();
        const form = e.target;
        const container = form.parentElement;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        ErrorHandler.clearErrors(container);
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Client-side validation
        const errors = FormValidator.validateForm(form, {
            email: [
                { type: 'required', message: 'Email is required' },
                { type: 'email', message: 'Please enter a valid email' }
            ],
            password: [
                { type: 'required', message: 'Password is required' }
            ]
        });
        
        if (Object.keys(errors).length > 0) {
            ErrorHandler.showFieldErrors(form, errors);
            return;
        }

        ErrorHandler.showLoading(submitBtn, 'Signing in...');
        
        try {
            const data = await EnhancedAPI.post('/auth/login', { email, password });
            
            if (data.success !== false) {
                this.setAuth(data.token, data.user);
                ErrorHandler.showError(container, 'Login successful! Redirecting...', 'success');
                setTimeout(() => window.location.href = '/dashboard', 1000);
            }
        } catch (error) {
            ErrorHandler.handleApiError(error, container, form);
        } finally {
            ErrorHandler.hideLoading(submitBtn);
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;
        const container = form.parentElement;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        ErrorHandler.clearErrors(container);
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // Client-side validation
        const errors = FormValidator.validateForm(form, {
            name: [
                { type: 'required', message: 'Name is required' }
            ],
            email: [
                { type: 'required', message: 'Email is required' },
                { type: 'email', message: 'Please enter a valid email' }
            ],
            password: [
                { type: 'required', message: 'Password is required' },
                { type: 'minLength', value: 6, message: 'Password must be at least 6 characters' }
            ],
            confirmPassword: [
                { type: 'required', message: 'Please confirm your password' },
                { type: 'match', field: '#password', message: 'Passwords do not match' }
            ]
        });
        
        if (Object.keys(errors).length > 0) {
            ErrorHandler.showFieldErrors(form, errors);
            return;
        }

        ErrorHandler.showLoading(submitBtn, 'Creating account...');
        
        try {
            const data = await EnhancedAPI.post('/auth/register', { name, email, password });
            
            if (data.success !== false) {
                this.setAuth(data.token, data.user);
                ErrorHandler.showError(container, 'Account created successfully! Redirecting...', 'success');
                setTimeout(() => window.location.href = '/dashboard', 1000);
            }
        } catch (error) {
            ErrorHandler.handleApiError(error, container, form);
        } finally {
            ErrorHandler.hideLoading(submitBtn);
        }
    }



    validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }



    setAuth(token, user) {
        this.token = token;
        this.user = user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
    }

    isAuthenticated() {
        return !!this.token;
    }

    updateNavigation() {
        const navMenu = document.getElementById('navMenu');
        if (!navMenu) return;

        if (this.isAuthenticated()) {
            navMenu.innerHTML = `
                <a href="/dashboard">Dashboard</a>
                <a href="/profile">${this.user?.name || 'Profile'}</a>
                <button onclick="auth.logout()" class="btn-outline">Logout</button>
            `;
        }
    }

    getAuthHeaders() {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }
}

// Initialize auth
const auth = new Auth();

// Redirect if already authenticated
if (auth.isAuthenticated() && (window.location.pathname === '/login' || window.location.pathname === '/register')) {
    window.location.href = '/dashboard';
}