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
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning("Unauthorized access", extra=get_error_context())
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning("Forbidden access", extra=get_error_context())
        return jsonify({'error': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning("Resource not found", extra=get_error_context())
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        context = get_error_context()
        logger.error("Internal server error", extra=context, exc_info=True)
        capture_exception(error, context)
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        context = get_error_context()
        logger.error("Database error", extra=context, exc_info=True)
        capture_exception(error, context)
        return jsonify({'error': 'Database error occurred'}), 500
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        context = get_error_context()
        logger.error("Database integrity error", extra=context)
        capture_exception(error, context)
        return jsonify({'error': 'Data integrity violation'}), 400