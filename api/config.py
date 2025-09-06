import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @staticmethod
    def get_database_uri():
        # Check for Vercel PostgreSQL URL first
        database_url = os.getenv('POSTGRES_URL')
        if not database_url:
            database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Handle both postgres:// and postgresql:// schemes
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        
        # Only use SQLite for local development
        if os.getenv('FLASK_ENV') == 'development':
            return 'sqlite:///synergysphere.db'
        
        # In production, database URL is required
        raise ValueError('Database URL is required in production environment')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Config.get_database_uri()

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}