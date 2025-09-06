
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Project, User, ProjectMember
from .validation import validate_json
from .query_utils import get_user_projects_query
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_project
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, error_response, not_found_response, access_denied_response, created_response


projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
@jwt_required()
@safe_db_operation("fetch projects")
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
@safe_db_operation("create project")
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
        
        return jsonify({'message': 'Member added successfully'})
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error adding member to project {project_id}: {e}")
        return jsonify({'error': 'Member already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error adding member to project {project_id}: {e}")
        return jsonify({'error': 'Failed to add member'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error adding member to project {project_id}: {e}")
        return jsonify({'error': 'Failed to add member'}), 500
