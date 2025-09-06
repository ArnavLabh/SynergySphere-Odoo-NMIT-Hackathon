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
            <div class="project-card">
                <div class="project-header">
                    <h3 onclick="projects.openProject(${project.id})" style="cursor: pointer;">${project.name}</h3>
                    <div class="project-actions">
                        <button onclick="projects.editProject(${project.id})" class="btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">Edit</button>
                        <button onclick="projects.deleteProject(${project.id})" class="btn-outline" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; color: #e53e3e; border-color: #e53e3e;">Delete</button>
                    </div>
                </div>
                <p class="project-description">${project.description || 'No description'}</p>
                <div class="project-stats">
                    <span class="stat">📋 Tasks</span>
                    <span class="stat">💬 Messages</span>
                </div>
                <span class="project-date">${new Date(project.created_at).toLocaleDateString()}</span>
            </div>
        `).join('');
    }

    showCreateModal() {
        document.getElementById('createProjectModal').style.display = 'flex';
    }

    hideCreateModal() {
        document.getElementById('createProjectModal').style.display = 'none';
        document.getElementById('createProjectForm').reset();
        
        // Reset modal to create mode
        this.editingProjectId = null;
        document.getElementById('createProjectTitle').textContent = 'Create New Project';
        document.querySelector('#createProjectForm button[type="submit"]').textContent = 'Create Project';
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
        
        try {
            let response;
            if (this.editingProjectId) {
                // Update existing project
                submitBtn.textContent = 'Updating...';
                response = await fetch(`/api/projects/${this.editingProjectId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, description })
                });
            } else {
                // Create new project
                submitBtn.textContent = 'Creating...';
                response = await fetch('/api/projects', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, description })
                });
            }
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || `HTTP ${response.status}`);
            }
            
            this.hideCreateModal();
            this.loadProjects();
            
            const action = this.editingProjectId ? 'updated' : 'created';
            if (window.AccessibilityManager) {
                window.AccessibilityManager.announce(`Project ${action} successfully`);
            }
        } catch (error) {
            this.showError(error.message || 'Failed to save project');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = this.editingProjectId ? 'Update Project' : 'Create Project';
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
        } else {
            alert(message);
        }
    }

    async editProject(projectId) {
        try {
            const response = await fetch(`/api/projects/${projectId}`);
            const project = await response.json();
            
            if (!response.ok) {
                throw new Error(project.error);
            }
            
            // Pre-fill the form with existing data
            document.getElementById('projectName').value = project.name;
            document.getElementById('projectDescription').value = project.description || '';
            
            // Store the project ID for updating
            this.editingProjectId = projectId;
            
            // Change modal title and button text
            document.getElementById('createProjectTitle').textContent = 'Edit Project';
            document.querySelector('#createProjectForm button[type="submit"]').textContent = 'Update Project';
            
            this.showCreateModal();
        } catch (error) {
            this.showError('Failed to load project details');
        }
    }
    
    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project? This will also delete all tasks and messages.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/projects/${projectId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error);
            }
            
            this.loadProjects();
            
            if (window.AccessibilityManager) {
                window.AccessibilityManager.announce('Project deleted successfully');
            }
        } catch (error) {
            this.showError('Failed to delete project');
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