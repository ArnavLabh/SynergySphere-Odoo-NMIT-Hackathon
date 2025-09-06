// Project Management
class Projects {
    constructor() {
        this.currentProject = null;
        this.projects = [];
    }

    init() {
        this.loadProjects();
        this.setupEventListeners();
        this.setupMobileMenu();
    }

    setupEventListeners() {
        const createForm = document.getElementById('createProjectForm');
        if (createForm) {
            createForm.addEventListener('submit', this.handleCreateProject.bind(this));
        }
    }

    setupMobileMenu() {
        const hamburger = document.getElementById('hamburger');
        const navLinks = document.getElementById('navLinks');
        
        if (hamburger && navLinks) {
            hamburger.addEventListener('click', () => {
                navLinks.classList.toggle('active');
                hamburger.classList.toggle('active');
            });
        }
    }

    async loadProjects() {
        try {
            const response = await API.get('/projects');
            this.projects = response.projects || [];
            this.renderProjects();
        } catch (error) {
            console.error('Load projects error:', error);
            this.projects = [];
            this.renderProjects();
        }
    }

    renderProjects() {
        const grid = document.getElementById('projectsGrid');
        if (!grid) return;

        if (this.projects.length === 0) {
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📁</div>
                    <h3>No projects yet</h3>
                    <p>Create your first project to get started</p>
                    <button class="btn-primary" onclick="projects.showCreateModal()">Create Project</button>
                </div>
            `;
            return;
        }

        grid.innerHTML = this.projects.map(project => `
            <div class="project-card" onclick="projects.openProject(${project.id})">
                <div class="project-header">
                    <h3>${project.name}</h3>
                    <span class="project-date">${new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                <p class="project-description">${project.description || 'No description'}</p>
                <div class="project-stats">
                    <span class="stat">📋 Tasks</span>
                    <span class="stat">💬 Messages</span>
                </div>
            </div>
        `).join('');
    }

    showCreateModal() {
        document.getElementById('createProjectModal').style.display = 'flex';
    }

    hideCreateModal() {
        document.getElementById('createProjectModal').style.display = 'none';
        document.getElementById('createProjectForm').reset();
    }

    async handleCreateProject(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        const name = document.getElementById('projectName').value.trim();
        const description = document.getElementById('projectDescription').value.trim();

        if (!name) {
            this.showError('Project name is required');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Creating...';
        
        try {
            // Use API class which includes authentication headers
            const result = await API.post('/projects', { name, description });
            
            this.hideCreateModal();
            this.loadProjects();
            
            // Show success notification
            if (window.notifications) {
                window.notifications.projectCreated(name);
            }
            
            if (window.AccessibilityManager) {
                window.AccessibilityManager.announce('Project created successfully');
            }
        } catch (error) {
            const errorMsg = error.message || 'Failed to create project';
            this.showError(errorMsg);
            if (window.notifications) {
                window.notifications.error(errorMsg);
            }
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Project';
        }
    }

    async openProject(projectId) {
        try {
            this.currentProject = await API.get(`/projects/${projectId}`);
            this.showProjectDetail();
            tasks.loadTasks(projectId);
            messages.loadMessages(projectId);
        } catch (error) {
            this.showError('Failed to load project');
        }
    }

    showProjectDetail() {
        document.querySelector('.dashboard-grid').style.display = 'none';
        document.getElementById('projectDetail').style.display = 'block';
        document.getElementById('projectTitle').textContent = this.currentProject.name;
    }

    hideDetail() {
        document.querySelector('.dashboard-grid').style.display = 'block';
        document.getElementById('projectDetail').style.display = 'none';
        this.currentProject = null;
    }

    showTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-selected', 'false');
        });
        event.target.classList.add('active');
        event.target.setAttribute('aria-selected', 'true');

        // Show/hide tab content
        document.getElementById('tasksTab').style.display = tabName === 'tasks' ? 'block' : 'none';
        document.getElementById('messagesTab').style.display = tabName === 'messages' ? 'block' : 'none';
    }

    showError(message) {
        const errorDiv = document.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => errorDiv.style.display = 'none', 5000);
        }
        
        // Also show notification if available
        if (window.notifications) {
            window.notifications.error(message);
        } else {
            alert(message);
        }
    }

    async testBackend() {
        try {
            const response = await fetch('/api/test');
            const result = await response.json();
            console.log('Backend test result:', result);
            alert('Backend is working: ' + result.message);
        } catch (error) {
            console.error('Backend test failed:', error);
            alert('Backend test failed: ' + error.message);
        }
    }
}

// Initialize projects
const projects = new Projects();