from flask import Blueprint, request, jsonify
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from .models import db, Message
from .validation import validate_json
from .permissions import require_project_access
from .pagination import get_pagination_params, format_pagination_response
from .serializers import serialize_message

logger = logging.getLogger(__name__)

messages_bp = Blueprint('messages', __name__)



@messages_bp.route('/api/projects/<int:project_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(project_id):
    try:
        user_id = get_jwt_identity()
        
        access_error = require_project_access(project_id, user_id)
        if access_error:
            return access_error
        
        page, per_page = get_pagination_params(default_per_page=50)
        
        # Eager load user to avoid N+1 queries
        messages_query = Message.query.options(joinedload(Message.user)).filter_by(project_id=project_id).order_by(Message.created_at.asc())
        messages_paginated = messages_query.paginate(page=page, per_page=per_page, error_out=False)
        
        response = format_pagination_response(messages_paginated, 'messages')
        response['messages'] = [serialize_message(msg) for msg in messages_paginated.items]
        
        return jsonify(response)
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching messages for project {project_id}: {e}")
        return jsonify({'error': 'Failed to fetch messages'}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching messages for project {project_id}: {e}")
        return jsonify({'error': 'Failed to fetch messages'}), 500

@messages_bp.route('/api/projects/<int:project_id>/messages', methods=['POST'])
@jwt_required()
def create_message(project_id):
    try:
        user_id = get_jwt_identity()
        
        access_error = require_project_access(project_id, user_id)
        if access_error:
            return access_error
        
        data = request.get_json()
        
        error = validate_json(data, ['content'])
        if error:
            return error
        
        message = Message(
            project_id=project_id,
            user_id=user_id,
            content=data['content'],
            parent_id=data.get('parent_id')  # for threading
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Refresh to get user relationship loaded
        db.session.refresh(message)
        
        return jsonify(serialize_message(message)), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error creating message for project {project_id}: {e}")
        return jsonify({'error': 'Failed to create message'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error creating message for project {project_id}: {e}")
        return jsonify({'error': 'Failed to create message'}), 500