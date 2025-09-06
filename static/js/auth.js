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
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!this.validateEmail(email)) {
            this.showError('Please enter a valid email');
            return;
        }

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.setAuth(data.token, data.user);
                window.location.href = '/dashboard';
            } else {
                this.showError(data.error || 'Login failed');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (!this.validateRegister(name, email, password, confirmPassword)) return;

        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.setAuth(data.token, data.user);
                window.location.href = '/dashboard';
            } else {
                this.showError(data.error || 'Registration failed');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        }
    }

    validateRegister(name, email, password, confirmPassword) {
        if (!name.trim()) {
            this.showError('Name is required');
            return false;
        }
        if (!this.validateEmail(email)) {
            this.showError('Please enter a valid email');
            return false;
        }
        if (password.length < 6) {
            this.showError('Password must be at least 6 characters');
            return false;
        }
        if (password !== confirmPassword) {
            this.showError('Passwords do not match');
            return false;
        }
        return true;
    }

    validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
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