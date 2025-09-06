// Task Management
class Tasks {
    constructor() {
        this.tasks = [];
        this.currentProjectId = null;
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const createForm = document.getElementById('createTaskForm');
        if (createForm) {
            createForm.addEventListener('submit', this.handleCreateTask.bind(this));
        }
    }

    async loadTasks(projectId) {
        this.currentProjectId = projectId;
        try {
            const response = await fetch(`/api/projects/${projectId}/tasks`);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error);
            }
            
            this.tasks = result.tasks || [];
            this.renderTasks();
            this.updateProgress();
        } catch (error) {
            this.showError('Failed to load tasks');
        }
    }

    renderTasks() {
        const todoList = document.getElementById('todoTasks');
        const inProgressList = document.getElementById('inProgressTasks');
        const doneList = document.getElementById('doneTasks');

        if (!todoList || !inProgressList || !doneList) return;

        // Clear existing tasks
        todoList.innerHTML = '';
        inProgressList.innerHTML = '';
        doneList.innerHTML = '';

        // Group tasks by status
        const todoTasks = this.tasks.filter(task => task.status === 'todo');
        const inProgressTasks = this.tasks.filter(task => task.status === 'in_progress');
        const doneTasks = this.tasks.filter(task => task.status === 'done');

        // Render tasks in each column
        this.renderTaskList(todoList, todoTasks);
        this.renderTaskList(inProgressList, inProgressTasks);
        this.renderTaskList(doneList, doneTasks);
    }

    renderTaskList(container, tasks) {
        if (tasks.length === 0) {
            container.innerHTML = '<div class="empty-column">No tasks</div>';
            return;
        }

        container.innerHTML = tasks.map(task => `
            <div class="task-card" draggable="true" data-task-id="${task.id}">
                <div class="task-header">
                    <h4>${task.title}</h4>
                    <div class="task-actions">
                        <select onchange="tasks.updateTaskStatus(${task.id}, this.value)" class="status-select">
                            <option value="todo" ${task.status === 'todo' ? 'selected' : ''}>To Do</option>
                            <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                            <option value="done" ${task.status === 'done' ? 'selected' : ''}>Done</option>
                        </select>
                    </div>
                </div>
                <p class="task-description">${task.description || 'No description'}</p>
                <div class="task-meta">
                    ${task.assignee_id ? `<span class="assignee">👤 ${task.assignee_name || 'Assigned'}</span>` : ''}
                    ${task.due_date ? `<span class="due-date ${this.isOverdue(task.due_date) ? 'overdue' : ''}">${this.formatDate(task.due_date)}</span>` : ''}
                </div>
            </div>
        `).join('');

        // Add drag and drop functionality
        this.setupDragAndDrop(container);
    }

    setupDragAndDrop(container) {
        const taskCards = container.querySelectorAll('.task-card');
        
        taskCards.forEach(card => {
            card.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', card.dataset.taskId);
                card.classList.add('dragging');
            });

            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
            });
        });

        // Make columns drop targets
        document.querySelectorAll('.task-list').forEach(list => {
            list.addEventListener('dragover', (e) => {
                e.preventDefault();
                list.classList.add('drag-over');
            });

            list.addEventListener('dragleave', () => {
                list.classList.remove('drag-over');
            });

            list.addEventListener('drop', (e) => {
                e.preventDefault();
                list.classList.remove('drag-over');
                
                const taskId = e.dataTransfer.getData('text/plain');
                const newStatus = this.getStatusFromColumn(list.id);
                
                if (newStatus) {
                    this.updateTaskStatus(taskId, newStatus);
                }
            });
        });
    }

    getStatusFromColumn(columnId) {
        const statusMap = {
            'todoTasks': 'todo',
            'inProgressTasks': 'in_progress',
            'doneTasks': 'done'
        };
        return statusMap[columnId];
    }

    async updateTaskStatus(taskId, newStatus) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status: newStatus })
            });
            
            if (!response.ok) {
                throw new Error('Failed to update task');
            }
            
            // Update local task status
            const task = this.tasks.find(t => t.id == taskId);
            if (task) {
                task.status = newStatus;
                this.renderTasks();
                this.updateProgress();
            }
        } catch (error) {
            this.showError('Failed to update task status');
        }
    }

    updateProgress() {
        const totalTasks = this.tasks.length;
        const completedTasks = this.tasks.filter(task => task.status === 'done').length;
        const progress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        if (progressFill && progressText) {
            progressFill.style.width = `${progress}%`;
            progressText.textContent = `${progress}% Complete (${completedTasks}/${totalTasks} tasks)`;
        }
    }

    showCreateModal() {
        document.getElementById('createTaskModal').style.display = 'flex';
        this.loadAssigneeOptions();
    }

    hideCreateModal() {
        document.getElementById('createTaskModal').style.display = 'none';
        document.getElementById('createTaskForm').reset();
    }

    async loadAssigneeOptions() {
        const select = document.getElementById('taskAssignee');
        if (!select) return;

        // For now, just add the current user
        select.innerHTML = `
            <option value="">Assign to...</option>
            <option value="${auth.user.id}">${auth.user.name} (You)</option>
        `;
    }

    async handleCreateTask(e) {
        e.preventDefault();
        
        const title = document.getElementById('taskTitle').value;
        const description = document.getElementById('taskDescription').value;

        try {
            const response = await fetch(`/api/projects/${this.currentProjectId}/tasks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    description
                })
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error);
            }
            
            this.hideCreateModal();
            this.loadTasks(this.currentProjectId);
        } catch (error) {
            this.showError(error.message || 'Failed to create task');
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    isOverdue(dateString) {
        const dueDate = new Date(dateString);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return dueDate < today;
    }

    showError(message) {
        // Use accessible error display instead of alert
        const errorContainer = document.querySelector('[role="alert"]');
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
        } else {
            alert(message); // Fallback
        }
        
        // Announce error to screen readers
        if (window.AccessibilityManager) {
            window.AccessibilityManager.announce(`Error: ${message}`);
        }
    }

    updateTaskStatus(taskId, newStatus) {
        // Announce status change
        if (window.AccessibilityManager) {
            const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
            if (taskElement) {
                window.AccessibilityManager.updateTaskStatus(taskElement, newStatus);
            }
        }
    }
}

// Initialize tasks
const tasks = new Tasks();
tasks.init();