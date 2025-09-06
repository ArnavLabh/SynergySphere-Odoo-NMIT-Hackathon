#!/usr/bin/env python3
"""
Database migration script for SynergySphere
Run this to create/update database tables with PostgreSQL
"""

import os
from api.index import app, db

def migrate_database():
    """Create or update database tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ PostgreSQL database tables created successfully!")
            
            # Verify connection
            result = db.session.execute('SELECT version()').fetchone()
            print(f"📋 Connected to: {result[0]}")
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🚀 Starting PostgreSQL database migration...")
    success = migrate_database()
    
    if success:
        print("✨ Migration completed successfully!")
    else:
        print("💥 Migration failed!")
        exit(1)