from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from .models import db, Task
from .validation import validate_json
from .utils import utc_now, parse_datetime
from .permissions import require_project_access
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_task
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, not_found_response, created_response
from .notifications import notify_task_assignment, notify_task_status_change

tasks_bp = Blueprint('tasks', __name__)



@tasks_bp.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
@safe_db_operation("fetch tasks")
def get_tasks(project_id):
    user_id = get_jwt_identity()
    
    access_error = require_project_access(project_id, user_id)
    if access_error:
        return access_error
    
    page, per_page = get_pagination_params(default_per_page=20)
    
    tasks_query = Task.query.options(joinedload(Task.assignee)).filter_by(project_id=project_id)
    tasks_paginated = tasks_query.paginate(page=page, per_page=per_page, error_out=False)
    
    response = format_pagination_response(tasks_paginated, 'tasks')
    response['tasks'] = [serialize_task(task) for task in tasks_paginated.items]
    
    return success_response(response)

@tasks_bp.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
@safe_db_operation("create task")
def create_task(project_id):
    user_id = get_jwt_identity()
    
    access_error = require_project_access(project_id, user_id)
    if access_error:
        return access_error
    
    data = request.get_json()
    
    error = validate_json(data, ['title'])
    if error:
        return error
    
    task = Task(
        project_id=project_id,
        title=data['title'],
        description=data.get('description', ''),
        assignee_id=data.get('assignee_id'),
        due_date=parse_datetime(data.get('due_date')),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'todo')
    )
    
    db.session.add(task)
    db.session.commit()
    
    # Send notification if task is assigned
    if task.assignee_id:
        notify_task_assignment(task, task.assignee_id)
    
    return created_response(serialize_task(task))

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PATCH'])
@jwt_required()
@safe_db_operation("update task")
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.get(task_id)
    
    if not task:
        return not_found_response("Task")
    
    access_error = require_project_access(task.project_id, user_id)
    if access_error:
        return access_error
    
    data = request.get_json()
    
    old_status = task.status
    old_assignee = task.assignee_id
    
    if 'status' in data:
        task.status = data['status']
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']
    if 'due_date' in data:
        task.due_date = parse_datetime(data.get('due_date'))
    if 'priority' in data:
        task.priority = data['priority']
    
    task.updated_at = utc_now()
    db.session.commit()
    
    # Send notifications for changes
    if 'status' in data and old_status != task.status:
        notify_task_status_change(task, old_status, user_id)
    
    if 'assignee_id' in data and old_assignee != task.assignee_id and task.assignee_id:
        notify_task_assignment(task, task.assignee_id)
    
    return success_response(serialize_task(task))