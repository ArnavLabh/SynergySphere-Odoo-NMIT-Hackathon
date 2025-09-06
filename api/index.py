from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import create_app, init_database
from models import db
from auth import auth_bp

# Create Flask app with database configuration
app = create_app()
CORS(app)

# Initialize JWT
jwt = JWTManager(app)

# Initialize database
db = init_database(app)

# Register blueprints
app.register_blueprint(auth_bp)
from projects import projects_bp
app.register_blueprint(projects_bp)

@app.route('/')
def index():
    return render_template('index.html')

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
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)