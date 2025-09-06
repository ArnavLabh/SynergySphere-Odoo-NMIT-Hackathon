from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Project, User

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
@jwt_required()
def get_projects():
    try:
        user_id = get_jwt_identity()
        projects = Project.query.filter_by(owner_id=user_id).all()
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'created_at': p.created_at.isoformat()
        } for p in projects])
    except Exception as e:
        return jsonify({'error': 'Failed to fetch projects'}), 500

@projects_bp.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
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
        return jsonify({'error': 'Failed to create project'}), 500

@projects_bp.route('/api/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch project'}), 500