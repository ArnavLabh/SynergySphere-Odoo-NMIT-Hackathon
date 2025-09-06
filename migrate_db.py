#!/usr/bin/env python3
"""
Database initialization script for SynergySphere
Use Flask-Migrate for proper database migrations
"""

from app import app
from api.models import db

def init_database():
    """Initialize database connection and verify setup"""
    
    with app.app_context():
        try:
            # Test database connection
            result = db.session.execute('SELECT version()').fetchone()
            print(f"✅ Connected to: {result[0]}")
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"📋 Found {len(tables)} tables: {', '.join(sorted(tables))}")
            else:
                print("⚠️  No tables found. Run 'flask db upgrade' to create tables.")
            
            return True
            
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False

if __name__ == '__main__':
    print("🚀 Checking database connection...")
    success = init_database()
    
    if success:
        print("✨ Database check completed!")
    else:
        print("💥 Database check failed!")
        exit(1)