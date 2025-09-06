
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import db, Project, User, ProjectMember, Task, Message
from .validation import validate_json
from .query_utils import get_user_projects_query
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_project
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, error_response, not_found_response, access_denied_response, created_response

logger = logging.getLogger(__name__)


projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Backend is working', 'timestamp': datetime.now().isoformat()})

@projects_bp.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        # For now, use user_id = 1 for testing
        user_id = 1
        projects = Project.query.filter_by(owner_id=user_id).all()
        return jsonify({
            'projects': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'created_at': p.created_at.isoformat()
            } for p in projects]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects', methods=['POST'])
def create_project():
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        # For now, use user_id = 1 for testing
        user_id = 1
        
        project = Project(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            owner_id=user_id
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        project.name = data['name'].strip()
        project.description = data.get('description', '').strip()
        
        db.session.commit()
        
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'updated_at': datetime.now().isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Delete related tasks and messages first
        Task.query.filter_by(project_id=project_id).delete()
        Message.query.filter_by(project_id=project_id).delete()
        ProjectMember.query.filter_by(project_id=project_id).delete()
        
        # Delete the project
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Tasks endpoints
@projects_bp.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
def get_tasks(project_id):
    try:
        tasks = Task.query.filter_by(project_id=project_id).all()
        return jsonify({
            'tasks': [{
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'assignee_id': t.assignee_id,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'created_at': t.created_at.isoformat()
            } for t in tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
def create_task(project_id):
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Task title is required'}), 400
        
        task = Task(
            project_id=project_id,
            title=data['title'].strip(),
            description=data.get('description', '').strip(),
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            assignee_id=data.get('assignee_id')
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'created_at': task.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/tasks/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        if 'status' in data:
            task.status = data['status']
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'updated_at': task.updated_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Messages endpoints
@projects_bp.route('/api/projects/<int:project_id>/messages', methods=['GET'])
def get_messages(project_id):
    try:
        messages = Message.query.filter_by(project_id=project_id).order_by(Message.created_at).all()
        return jsonify({
            'messages': [{
                'id': m.id,
                'content': m.content,
                'user_id': m.user_id,
                'created_at': m.created_at.isoformat()
            } for m in messages]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>/messages', methods=['POST'])
def create_message(project_id):
    try:
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'error': 'Message content is required'}), 400
        
        # Use user_id = 1 for testing
        user_id = 1
        
        message = Message(
            project_id=project_id,
            user_id=user_id,
            content=data['content'].strip()
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'id': message.id,
            'content': message.content,
            'user_id': message.user_id,
            'created_at': message.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
