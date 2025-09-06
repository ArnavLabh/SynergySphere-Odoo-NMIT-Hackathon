
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import db, Project, User, ProjectMember
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
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        # Extract and decode token
        token = auth_header.split(' ')[1]
        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
        except Exception as jwt_error:
            logger.error(f"JWT decode error: {jwt_error}")
            return jsonify({'error': 'Invalid token'}), 401
        
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
        logger.error(f"Get projects error: {e}")
        return jsonify({'error': 'Failed to fetch projects'}), 500

@projects_bp.route('/api/projects', methods=['POST'])
def create_project():
    try:
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        # Extract token
        token = auth_header.split(' ')[1]
        logger.info(f"Received token: {token[:20]}...")
        
        # Verify JWT manually for debugging
        from flask_jwt_extended import decode_token
        try:
            decoded = decode_token(token)
            user_id = decoded['sub']
            logger.info(f"Decoded user_id: {user_id}")
        except Exception as jwt_error:
            logger.error(f"JWT decode error: {jwt_error}")
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        project = Project(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            owner_id=user_id
        )
        
        db.session.add(project)
        db.session.commit()
        logger.info(f"Project created successfully: {project.id}")
        
        return jsonify({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat()
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Project creation error: {e}")
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500

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
