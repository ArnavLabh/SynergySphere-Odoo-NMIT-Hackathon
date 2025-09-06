from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def utc_now():
    """Return current UTC datetime"""
    return datetime.now(timezone.utc)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='employee')  # manager, employee, admin
    created_at = db.Column(db.DateTime, default=utc_now)
    
    # Relationships
    owned_projects = db.relationship('Project', backref='owner', lazy='dynamic')
    assigned_tasks = db.relationship('Task', backref='assignee', lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy='dynamic')
    messages = db.relationship('Message', backref='project', lazy='dynamic')
    members = db.relationship('ProjectMember', backref='project', lazy='dynamic')

class ProjectMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    role = db.Column(db.String(20), default='member', index=True)  # owner, admin, member
    created_at = db.Column(db.DateTime, default=utc_now)
    
    __table_args__ = (db.Index('ix_project_member_composite', 'project_id', 'user_id'),)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    due_date = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(20), default='todo', index=True)  # todo, in_progress, done
    priority = db.Column(db.String(10), default='medium', index=True)  # low, medium, high
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now, index=True)
    
    __table_args__ = (
        db.Index('ix_task_project_status', 'project_id', 'status'),
        db.Index('ix_task_assignee_status', 'assignee_id', 'status'),
    )

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('message.id'), index=True)  # for threading
    created_at = db.Column(db.DateTime, default=utc_now, index=True)
    
    __table_args__ = (
        db.Index('ix_message_project_created', 'project_id', 'created_at'),
        db.Index('ix_message_thread', 'parent_id', 'created_at'),
    )