from flask import render_template, jsonify
from .models import db

def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/register')
    def register():
        return render_template('register.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    @app.route('/projects')
    def projects_page():
        return render_template('projects.html')
    
    @app.route('/projects/<int:project_id>')
    def project_detail(project_id):
        return render_template('project_detail.html')
    
    @app.route('/tasks')
    def tasks_page():
        return render_template('tasks.html')
    
    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route('/api/health')
    def api_health_check():
        """Health check including database connectivity"""
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
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