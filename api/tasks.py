from flask import Blueprint, request, jsonify
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from .models import db, Task
from .validation import validate_json
from .utils import utc_now, parse_datetime
from .permissions import require_project_access
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_task

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__)



@tasks_bp.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    try:
        user_id = get_jwt_identity()
        
        access_error = require_project_access(project_id, user_id)
        if access_error:
            return access_error
        
        page, per_page = get_pagination_params(default_per_page=20)
        
        tasks_query = Task.query.options(joinedload(Task.assignee)).filter_by(project_id=project_id)
        tasks_paginated = tasks_query.paginate(page=page, per_page=per_page, error_out=False)
        
        response = format_pagination_response(tasks_paginated, 'tasks')
        response['tasks'] = [serialize_task(task) for task in tasks_paginated.items]
        
        return jsonify(response)
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching tasks for project {project_id}: {e}")
        return jsonify({'error': 'Failed to fetch tasks'}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching tasks for project {project_id}: {e}")
        return jsonify({'error': 'Failed to fetch tasks'}), 500

@tasks_bp.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    try:
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
        
        return jsonify(serialize_task(task)), 201
    except ValueError as e:
        logger.error(f"Invalid date format in task creation: {e}")
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating task for project {project_id}: {e}")
        return jsonify({'error': 'Failed to create task'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating task for project {project_id}: {e}")
        return jsonify({'error': 'Failed to create task'}), 500

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        access_error = require_project_access(task.project_id, user_id)
        if access_error:
            return access_error
        
        data = request.get_json()
        
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
        
        return jsonify(serialize_task(task))
    except ValueError as e:
        logger.error(f"Invalid date format in task update: {e}")
        return jsonify({'error': 'Invalid date format'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error updating task {task_id}: {e}")
        return jsonify({'error': 'Failed to update task'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error updating task {task_id}: {e}")
        return jsonify({'error': 'Failed to update task'}), 500