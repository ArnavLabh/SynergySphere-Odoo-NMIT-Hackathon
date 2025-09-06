from flask import Flask, jsonify
from flask_cors import CORS
from database import create_app, init_database
from models import db

# Create Flask app with database configuration
app = create_app()
CORS(app)

# Initialize database
db = init_database(app)

@app.route('/')
def health_check():
    return jsonify({
        'status': 'ok', 
        'message': 'SynergySphere API',
        'version': '1.0.0'
    })

@app.route('/api/health')
def api_health_check():
    """Detailed health check including database connectivity"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'ok',
        'api_version': '1.0.0',
        'database': db_status,
        'message': 'SynergySphere API is running'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)