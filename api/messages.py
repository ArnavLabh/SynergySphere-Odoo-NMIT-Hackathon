from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Discussion, Project, User

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/api/projects/<int:project_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, created_by=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    messages = Discussion.query.filter_by(project_id=project_id).order_by(Discussion.created_at.asc()).all()
    
    return jsonify([{
        'id': msg.id,
        'message': msg.message,
        'user_id': msg.user_id,
        'user_name': User.query.get(msg.user_id).name if msg.user_id else 'Unknown',
        'created_at': msg.created_at.isoformat()
    } for msg in messages])

@messages_bp.route('/api/projects/<int:project_id>/messages', methods=['POST'])
@jwt_required()
def create_message(project_id):
    user_id = get_jwt_identity()
    project = Project.query.filter_by(id=project_id, created_by=user_id).first()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    
    message = Discussion(
        project_id=project_id,
        user_id=user_id,
        message=data['message']
    )
    
    db.session.add(message)
    db.session.commit()
    
    user = User.query.get(user_id)
    
    return jsonify({
        'id': message.id,
        'message': message.message,
        'user_id': message.user_id,
        'user_name': user.name if user else 'Unknown',
        'created_at': message.created_at.isoformat()
    }), 201
