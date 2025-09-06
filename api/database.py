import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Database Configuration for Neon/PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # For Neon database or any PostgreSQL connection
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to individual components
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        db_name = os.environ.get('DB_NAME', 'synergysphere')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', '')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    # SQLAlchemy configuration
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': -1,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 20
    }
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-this')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours
    
    return app

def init_database(app):
    """Initialize database with the app"""
    from .models import db, init_db
    init_db(app)
    return db