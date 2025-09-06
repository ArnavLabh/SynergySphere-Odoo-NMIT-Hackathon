#!/usr/bin/env python3
"""
Database migration script for SynergySphere
Run this script to create all database tables and indexes
"""

from database import create_app, init_database
from models import db, User, Project, ProjectMember, Task, Message
import os
import sys

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            # Initialize database
            db = init_database(app)
            
            print("✓ Database tables created successfully!")
            
            # Print table information
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\nCreated tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"  - {table}")
                
            print("\n✓ Database migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        sys.exit(1)

def drop_tables():
    """Drop all database tables (use with caution!)"""
    print("⚠️  WARNING: This will delete all data!")
    confirmation = input("Are you sure you want to drop all tables? (type 'yes' to confirm): ")
    
    if confirmation.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        app = create_app()
        
        with app.app_context():
            db = init_database(app)
            db.drop_all()
            print("✓ All tables dropped successfully!")
            
    except Exception as e:
        print(f"❌ Error dropping tables: {str(e)}")
        sys.exit(1)

def reset_database():
    """Reset the database by dropping and recreating all tables"""
    print("Resetting database...")
    
    try:
        app = create_app()
        
        with app.app_context():
            db = init_database(app)
            
            # Drop all tables
            print("Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("Creating new tables...")
            db.create_all()
            
            print("✓ Database reset completed successfully!")
            
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        sys.exit(1)

def seed_database():
    """Seed the database with sample data"""
    print("Seeding database with sample data...")
    
    try:
        app = create_app()
        
        with app.app_context():
            db = init_database(app)
            
            # Create sample users
            from werkzeug.security import generate_password_hash
            
            admin_user = User(
                name="Admin User",
                email="admin@synergysphere.com",
                password_hash=generate_password_hash("admin123")
            )
            
            test_user = User(
                name="Test User",
                email="test@synergysphere.com",
                password_hash=generate_password_hash("test123")
            )
            
            db.session.add(admin_user)
            db.session.add(test_user)
            db.session.commit()
            
            # Create sample project
            sample_project = Project(
                name="Sample Project",
                description="This is a sample project to test the system",
                owner_id=admin_user.id
            )
            
            db.session.add(sample_project)
            db.session.commit()
            
            # Add project member
            project_member = ProjectMember(
                project_id=sample_project.id,
                user_id=test_user.id,
                role="member"
            )
            
            db.session.add(project_member)
            
            # Create sample task
            sample_task = Task(
                project_id=sample_project.id,
                title="Setup Database Models",
                description="Create all necessary database models for the application",
                assignee_id=test_user.id,
                status="completed"
            )
            
            db.session.add(sample_task)
            
            # Create sample message
            sample_message = Message(
                project_id=sample_project.id,
                user_id=admin_user.id,
                content="Welcome to the SynergySphere project!"
            )
            
            db.session.add(sample_message)
            db.session.commit()
            
            print("✓ Sample data seeded successfully!")
            print(f"  - Created users: {admin_user.email}, {test_user.email}")
            print(f"  - Created project: {sample_project.name}")
            print(f"  - Created task: {sample_task.title}")
            print(f"  - Created message: Sample welcome message")
            
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [create|drop|reset|seed]")
        print("Commands:")
        print("  create - Create all database tables")
        print("  drop   - Drop all database tables")
        print("  reset  - Drop and recreate all tables")
        print("  seed   - Add sample data to database")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'create':
        create_tables()
    elif command == 'drop':
        drop_tables()
    elif command == 'reset':
        reset_database()
    elif command == 'seed':
        seed_database()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)