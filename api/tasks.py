from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Task, Project, User, ProjectMember
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

def check_project_access(project_id, user_id):
    """Check if user has access to project"""
    project = Project.query.get(project_id)
    if not project:
        return False
    
    is_owner = project.owner_id == user_id
    is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    
    return is_owner or is_member

@tasks_bp.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    try:
        user_id = get_jwt_identity()
        
        if not check_project_access(project_id, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        tasks = Task.query.filter_by(project_id=project_id).all()
        
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assignee_id': task.assignee_id,
            'assignee_name': User.query.get(task.assignee_id).name if task.assignee_id else None,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        } for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    try:
        user_id = get_jwt_identity()
        
        if not check_project_access(project_id, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        task = Task(
            project_id=project_id,
            title=data['title'],
            description=data.get('description', ''),
            assignee_id=data.get('assignee_id'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'todo')
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assignee_id': task.assignee_id,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PATCH'])
@jwt_required()
def update_task(task_id):
    try:
        user_id = get_jwt_identity()
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if not check_project_access(task.project_id, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
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
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        if 'priority' in data:
            task.priority = data['priority']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'assignee_id': task.assignee_id,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'priority': task.priority,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500