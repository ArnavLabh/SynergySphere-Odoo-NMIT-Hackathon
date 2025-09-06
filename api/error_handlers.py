import logging
from flask import jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import BadRequest, NotFound, Forbidden, Unauthorized

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register global error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request: {error}")
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"Unauthorized access: {error}")
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"Forbidden access: {error}")
        return jsonify({'error': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Resource not found: {error}")
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        logger.error(f"Database error: {error}")
        return jsonify({'error': 'Database error occurred'}), 500
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        logger.error(f"Database integrity error: {error}")
        return jsonify({'error': 'Data integrity violation'}), 400