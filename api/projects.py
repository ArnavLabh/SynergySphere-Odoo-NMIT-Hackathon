from flask import Blueprint, request, jsonify
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from .models import db, Project, User, ProjectMember
from .validation import validate_json
from .query_utils import get_user_projects_query
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_project

logger = logging.getLogger(__name__)

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
@jwt_required()
def get_projects():
    try:
        user_id = get_jwt_identity()
        
        page, per_page = get_pagination_params(default_per_page=20)
        
        # Use optimized query utility
        projects_query = get_user_projects_query(user_id)
        
        projects_paginated = projects_query.paginate(page=page, per_page=per_page, error_out=False)
        
        response = format_pagination_response(projects_paginated, 'projects')
        response['projects'] = [serialize_project(p) for p in projects_paginated.items]
        
        return jsonify(response)
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching projects for user {user_id}: {e}")
        return jsonify({'error': 'Failed to fetch projects'}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching projects for user {user_id}: {e}")
        return jsonify({'error': 'Failed to fetch projects'}), 500

@projects_bp.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        error = validate_json(data, ['name'])
        if error:
            return error
        
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
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error creating project: {e}")
        return jsonify({'error': 'Project name already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating project: {e}")
        return jsonify({'error': 'Failed to create project'}), 500
    except ValueError as e:
        logger.error(f"Validation error creating project: {e}")
        return jsonify({'error': 'Invalid project data'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating project: {e}")
        return jsonify({'error': 'Failed to create project'}), 500

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
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching project {project_id}: {e}")
        return jsonify({'error': 'Failed to fetch project'}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching project {project_id}: {e}")
        return jsonify({'error': 'Failed to fetch project'}), 500

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