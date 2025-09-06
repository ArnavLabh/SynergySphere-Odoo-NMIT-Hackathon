#!/usr/bin/env python3
"""
Database migration script for SynergySphere
Run this to create/update database tables
"""

from api.database import create_app
from api.models import db

def migrate_database():
    """Create or update database tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables exist
            tables = db.engine.table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🚀 Starting database migration...")
    success = migrate_database()
    
    if success:
        print("✨ Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        exit(1)