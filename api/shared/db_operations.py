import logging
from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from ..models import db
from .error_tracking import capture_exception

logger = logging.getLogger(__name__)

def safe_db_operation(operation_name="database operation"):
    """Decorator for safe database operations with structured logging"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get context for logging
            user_id = None
            try:
                user_id = get_jwt_identity()
            except:
                pass
            
            extra = {
                'operation': operation_name,
                'user_id': user_id,
                'request_id': getattr(g, 'request_id', None)
            }
            
            logger.info(f"Starting {operation_name}", extra=extra)
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_name}", extra=extra)
                return result
            except IntegrityError as e:
                db.session.rollback()
                logger.error(f"Integrity error in {operation_name}: {str(e)}", extra=extra)
                capture_exception(e, {'operation': operation_name, 'user_id': user_id})
                return jsonify({'error': 'Data already exists or constraint violation'}), 400
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Database error in {operation_name}: {str(e)}", extra=extra)
                capture_exception(e, {'operation': operation_name, 'user_id': user_id})
                return jsonify({'error': f'Database error in {operation_name}'}), 500
            except ValueError as e:
                logger.error(f"Validation error in {operation_name}: {str(e)}", extra=extra)
                return jsonify({'error': 'Invalid input data'}), 400
            except Exception as e:
                db.session.rollback()
                logger.error(f"Unexpected error in {operation_name}: {str(e)}", extra=extra, exc_info=True)
                capture_exception(e, {'operation': operation_name, 'user_id': user_id})
                return jsonify({'error': f'{operation_name.title()} failed'}), 500
        return wrapper
    return decorator

def commit_or_rollback():
    """Safely commit database changes"""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Commit failed: {e}")
        return False