#!/usr/bin/env python3
"""
Database setup script for SynergySphere
Run this to initialize the database with proper migrations
"""

import os
import subprocess
import sys
from api import create_app
from api.models import db

def setup_database():
    """Setup database with Flask-Migrate"""
    print("🚀 Setting up SynergySphere database...")
    
    # Set Flask app for CLI
    os.environ['FLASK_APP'] = 'app.py'
    
    try:
        from app import app
        
        with app.app_context():
            # Test database connection
            result = db.session.execute('SELECT version()').fetchone()
            print(f"✅ Connected to: {result[0]}")
            
            # Check if migrations folder exists
            if not os.path.exists('migrations'):
                print("📁 Initializing migrations...")
                subprocess.run(['flask', 'db', 'init'], check=True)
            
            # Create initial migration
            print("📝 Creating migration...")
            subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration'], check=True)
            
            # Apply migration
            print("⬆️  Applying migration...")
            subprocess.run(['flask', 'db', 'upgrade'], check=True)
            
            print("✨ Database setup completed successfully!")
            print("\nNext steps:")
            print("1. Run 'python api/migrate.py' to seed sample data")
            print("2. Run 'python flask_app.py' to start the development server")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    setup_database()