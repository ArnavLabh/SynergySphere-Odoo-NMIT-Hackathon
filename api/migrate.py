#!/usr/bin/env python3
"""
Database seeding script for SynergySphere
Use this to populate the database with sample data
"""

import sys
from app import app
from api.models import db, User, Project, ProjectMember, Task, Message
from werkzeug.security import generate_password_hash

def seed_database():
    """Seed the database with sample data"""
    print("Seeding database with sample data...")
    
    with app.app_context():
        try:
            # Create sample users
            
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
    seed_database()