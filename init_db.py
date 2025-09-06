#!/usr/bin/env python3
"""
Initialize database tables for production deployment
"""
import os
import sys
from api import create_app
from api.models import db

def init_database():
    """Initialize database tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test database connection
            from sqlalchemy import text
            result = db.session.execute(text("SELECT 1"))
            print("✅ Database connection verified!")
            
            # List created tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Created tables: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing database: {str(e)}")
            return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
