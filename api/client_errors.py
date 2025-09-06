from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)
client_errors_bp = Blueprint('client_errors', __name__)

@client_errors_bp.route('/api/client-errors', methods=['POST'])
def log_client_error():
    """Endpoint to receive client-side errors"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Log client error with structured format
        logger.error("Client-side error", extra={
            'client_message': data.get('message'),
            'client_url': data.get('url'),
            'client_user_agent': data.get('userAgent'),
            'client_timestamp': data.get('timestamp'),
            'client_context': data.get('context', {})
        })
        
        return '', 204
    except Exception as e:
        logger.error(f"Failed to log client error: {e}")
        return '', 204  # Always return success to avoid client retry loops