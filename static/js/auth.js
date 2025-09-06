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
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        if (!email || !password) {
            this.showError('Please fill in all fields');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Signing in...';
        
        try {
            const data = await API.post('/auth/login', { email, password });
            
            this.setAuth(data.token, data.user);
            window.location.href = '/dashboard';
        } catch (error) {
            this.showError(error.message || 'Login failed');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Sign In';
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (!name || !email || !password || !confirmPassword) {
            this.showError('Please fill in all fields');
            return;
        }
        
        if (password !== confirmPassword) {
            this.showError('Passwords do not match');
            return;
        }
        
        if (password.length < 6) {
            this.showError('Password must be at least 6 characters');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating account...';
        
        try {
            const data = await API.post('/auth/register', { name, email, password });
            
            this.setAuth(data.token, data.user);
            window.location.href = '/dashboard';
        } catch (error) {
            this.showError(error.message || 'Registration failed');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Account';
        }
    }



    showError(message) {
        const errorDiv = document.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => errorDiv.style.display = 'none', 5000);
        } else {
            alert(message);
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