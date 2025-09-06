from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Message, Project, User, ProjectMember

messages_bp = Blueprint('messages', __name__)

def check_project_access(project_id, user_id):
    """Check if user has access to project"""
    project = Project.query.get(project_id)
    if not project:
        return False
    
    is_owner = project.owner_id == user_id
    is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    
    return is_owner or is_member

@messages_bp.route('/api/projects/<int:project_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(project_id):
    try:
        user_id = get_jwt_identity()
        
        if not check_project_access(project_id, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        messages = Message.query.filter_by(project_id=project_id).order_by(Message.created_at.asc()).all()
        
        return jsonify([{
            'id': msg.id,
            'content': msg.content,
            'user_id': msg.user_id,
            'user_name': User.query.get(msg.user_id).name if msg.user_id else 'Unknown',
            'parent_id': msg.parent_id,
            'created_at': msg.created_at.isoformat()
        } for msg in messages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/api/projects/<int:project_id>/messages', methods=['POST'])
@jwt_required()
def create_message(project_id):
    try:
        user_id = get_jwt_identity()
        
        if not check_project_access(project_id, user_id):
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        message = Message(
            project_id=project_id,
            user_id=user_id,
            content=data['content'],
            parent_id=data.get('parent_id')  # for threading
        )
        
        db.session.add(message)
        db.session.commit()
        
        user = User.query.get(user_id)
        
        return jsonify({
            'id': message.id,
            'content': message.content,
            'user_id': message.user_id,
            'user_name': user.name if user else 'Unknown',
            'parent_id': message.parent_id,
            'created_at': message.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500