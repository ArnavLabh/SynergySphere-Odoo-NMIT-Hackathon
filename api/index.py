import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()

# Create Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Configuration
database_url = os.getenv('POSTGRES_URL', os.getenv('DATABASE_URL'))
if not database_url:
    raise ValueError('POSTGRES_URL environment variable is required')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

# Initialize extensions
CORS(app)
jwt = JWTManager(app)
db.init_app(app)

# Import models after db initialization
from .models import User, Project, Task, Message, ProjectMember

# Import and register blueprints
from .auth import auth_bp
from .projects import projects_bp
from .tasks import tasks_bp
from .messages import messages_bp

app.register_blueprint(auth_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(messages_bp)

# Create tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")

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

@app.route('/about')
def about():
    return render_template('about.html')

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
