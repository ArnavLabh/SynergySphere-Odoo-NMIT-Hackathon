from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import db
from .models import Project, User, ProjectMember

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
@jwt_required()
def get_projects():
    try:
        user_id = get_jwt_identity()
        # Get projects where user is owner or member
        owned_projects = Project.query.filter_by(owner_id=user_id).all()
        member_projects = db.session.query(Project).join(ProjectMember).filter(ProjectMember.user_id == user_id).all()
        
        all_projects = list(set(owned_projects + member_projects))
        
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'created_at': p.created_at.isoformat()
        } for p in all_projects])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
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
@jwt_required()
def get_project(project_id):
    try:
        user_id = get_jwt_identity()
        # Check if user is owner or member
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
            
        is_owner = project.owner_id == user_id
        is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
        
        if not (is_owner or is_member):
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@projects_bp.route('/api/projects/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_member(project_id):
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found or access denied'}), 404
        
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already a member
        existing = ProjectMember.query.filter_by(project_id=project_id, user_id=user.id).first()
        if existing:
            return jsonify({'error': 'User is already a member'}), 400
        
        # Add member
        member = ProjectMember(
            project_id=project_id,
            user_id=user.id,
            role=data.get('role', 'member')
        )
        
        db.session.add(member)
        db.session.commit()
        
        return jsonify({'message': 'Member added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500