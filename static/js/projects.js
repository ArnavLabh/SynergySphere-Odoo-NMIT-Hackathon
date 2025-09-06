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
            this.projects = await API.get('/projects');
            this.renderProjects();
        } catch (error) {
            console.error('Load projects error:', error);
            // Don't show error for empty projects, just render empty state
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
        const modal = document.getElementById('createProjectModal');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        ErrorHandler.clearErrors(modal);
        
        const name = document.getElementById('projectName').value.trim();
        const description = document.getElementById('projectDescription').value.trim();

        // Client-side validation
        const errors = FormValidator.validateForm(form, {
            projectName: [
                { type: 'required', message: 'Project name is required' }
            ]
        });
        
        if (Object.keys(errors).length > 0) {
            ErrorHandler.showFieldErrors(form, errors);
            return;
        }

        ErrorHandler.showLoading(submitBtn, 'Creating...');
        
        try {
            const result = await EnhancedAPI.post('/projects', { name, description });
            
            if (result.success !== false) {
                ErrorHandler.showError(modal, 'Project created successfully!', 'success');
                setTimeout(() => {
                    this.hideCreateModal();
                    this.loadProjects();
                }, 1000);
            }
        } catch (error) {
            ErrorHandler.handleApiError(error, modal, form);
        } finally {
            ErrorHandler.hideLoading(submitBtn);
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
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        // Show/hide tab content
        document.getElementById('tasksTab').style.display = tabName === 'tasks' ? 'block' : 'none';
        document.getElementById('messagesTab').style.display = tabName === 'messages' ? 'block' : 'none';
    }


}

// Initialize projects
const projects = new Projects();