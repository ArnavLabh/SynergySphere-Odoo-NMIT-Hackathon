import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .models import db
from .config import config
from .error_handlers import register_error_handlers

def create_app(config_name=None):
    """Application factory with centralized configuration"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    Migrate(app, db)
    
    # Register blueprints
    from .auth import auth_bp
    from .projects import projects_bp
    from .tasks import tasks_bp
    from .messages import messages_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(messages_bp)
    
    # Register routes
    from . import routes
    routes.register_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s'
        )
    
    return app