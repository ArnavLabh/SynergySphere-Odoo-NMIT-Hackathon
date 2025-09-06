
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import db, Project, User, ProjectMember, Task, Message, Notification
from .validation import validate_json
from .query_utils import get_user_projects_query
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_project
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, error_response, not_found_response, access_denied_response, created_response
from .notifications import notify_project_member_added

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
@jwt_required()
@safe_db_operation("fetch project")
def get_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return not_found_response("Project")
        
    is_owner = project.owner_id == user_id
    is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    
    if not (is_owner or is_member):
        return access_denied_response()
    
    return success_response({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at.isoformat()
    })

@projects_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
@safe_db_operation("update project")
def update_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return not_found_response("Project")
    
    # Only owner can update project
    if project.owner_id != user_id:
        return access_denied_response()
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name'].strip()
    if 'description' in data:
        project.description = data['description'].strip()
    
    db.session.commit()
    
    return success_response({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at.isoformat()
    })

@projects_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
@safe_db_operation("delete project")
def delete_project(project_id):
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return not_found_response("Project")
    
    # Only owner can delete project
    if project.owner_id != user_id:
        return access_denied_response()
    
    # Delete all related data
    ProjectMember.query.filter_by(project_id=project_id).delete()
    Task.query.filter_by(project_id=project_id).delete()
    Message.query.filter_by(project_id=project_id).delete()
    Notification.query.filter_by(related_project_id=project_id).delete()
    
    db.session.delete(project)
    db.session.commit()
    
    return success_response({'message': 'Project deleted successfully'})

@projects_bp.route('/api/projects/<int:project_id>/members', methods=['GET'])
@jwt_required()
@safe_db_operation("get project members")
def get_project_members(project_id):
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return not_found_response("Project")
    
    # Check if user has access to this project
    is_owner = project.owner_id == user_id
    is_member = ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()
    
    if not (is_owner or is_member):
        return access_denied_response()
    
    # Get all members
    members = db.session.query(User, ProjectMember).join(
        ProjectMember, User.id == ProjectMember.user_id
    ).filter(ProjectMember.project_id == project_id).all()
    
    # Add owner to the list
    owner = User.query.get(project.owner_id)
    
    member_list = [{
        'id': owner.id,
        'name': owner.name,
        'email': owner.email,
        'role': 'owner',
        'is_owner': True
    }]
    
    for user, member in members:
        member_list.append({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': member.role,
            'is_owner': False
        })
    
    return success_response({'members': member_list})

@projects_bp.route('/api/projects/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_member(project_id):
    try:
        user_id = get_jwt_identity()
        project = Project.query.filter_by(id=project_id, owner_id=user_id).first()
        
        if not project:
            return jsonify({'error': 'Project not found or access denied'}), 404
        
        data = request.get_json()
        
        error = validate_json(data, ['email'])
        if error:
            return error
        
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
        
        # Get the name of the user who added the member
        adder = User.query.get(user_id)
        if adder:
            notify_project_member_added(project_id, user.id, adder.name)
        
        return jsonify({'message': 'Member added successfully'})
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error adding member to project {project_id}: {e}")
        return jsonify({'error': 'Member already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error adding member to project {project_id}: {e}")
        return jsonify({'error': 'Failed to add member'}), 500

@projects_bp.route('/api/projects/<int:project_id>/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
@safe_db_operation("remove project member")
def remove_member(project_id, member_id):
    user_id = get_jwt_identity()
    project = Project.query.get(project_id)
    
    if not project:
        return not_found_response("Project")
    
    # Only owner can remove members
    if project.owner_id != user_id:
        return access_denied_response()
    
    # Cannot remove the owner
    if member_id == project.owner_id:
        return error_response('Cannot remove project owner', 400)
    
    member = ProjectMember.query.filter_by(project_id=project_id, user_id=member_id).first()
    
    if not member:
        return not_found_response("Member")
    
    db.session.delete(member)
    db.session.commit()
    
    return success_response({'message': 'Member removed successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error adding member to project {project_id}: {e}")
        return jsonify({'error': 'Failed to add member'}), 500
