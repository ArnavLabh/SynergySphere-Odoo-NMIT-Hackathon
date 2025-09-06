import logging
from flask import jsonify, request, g
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound, Forbidden, Unauthorized
from .shared.error_tracking import capture_exception

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register global error handlers with structured logging"""
    
    def get_error_context():
        return {
            'endpoint': request.endpoint if request else None,
            'method': request.method if request else None,
            'url': request.url if request else None,
            'request_id': getattr(g, 'request_id', None)
        }
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning("Bad request", extra=get_error_context())
        return jsonify({'success': False, 'error': 'Bad request', 'error_code': 'BAD_REQUEST'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning("Unauthorized access", extra=get_error_context())
        return jsonify({'success': False, 'error': 'Unauthorized', 'error_code': 'UNAUTHORIZED'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning("Forbidden access", extra=get_error_context())
        return jsonify({'success': False, 'error': 'Access denied', 'error_code': 'FORBIDDEN'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning("Resource not found", extra=get_error_context())
        return jsonify({'success': False, 'error': 'Resource not found', 'error_code': 'NOT_FOUND'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        context = get_error_context()
        logger.error("Internal server error", extra=context, exc_info=True)
        capture_exception(error, context)
        return jsonify({'success': False, 'error': 'Internal server error', 'error_code': 'INTERNAL_ERROR'}), 500
    
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        context = get_error_context()
        logger.error("Database error", extra=context, exc_info=True)
        capture_exception(error, context)
        return jsonify({'success': False, 'error': 'Database error occurred', 'error_code': 'DATABASE_ERROR'}), 500
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        context = get_error_context()
        logger.error("Database integrity error", extra=context)
        capture_exception(error, context)
        return jsonify({'success': False, 'error': 'Data integrity violation', 'error_code': 'INTEGRITY_ERROR'}), 400