from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"

class ProjectRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    owned_projects = db.relationship('Project', foreign_keys='Project.owner_id', backref='owner', lazy='dynamic')
    project_memberships = db.relationship('ProjectMember', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee', lazy='dynamic')
    messages = db.relationship('Message', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('ProjectMember', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'owner_name': self.owner.name if self.owner else None
        }

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.Enum(ProjectRole), nullable=False, default=ProjectRole.MEMBER)
    
    # Unique constraint to prevent duplicate memberships
    __table_args__ = (db.UniqueConstraint('project_id', 'user_id', name='_project_user_uc'),)
    
    def __repr__(self):
        return f'<ProjectMember {self.user.name} in {self.project.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role.value,
            'user_name': self.user.name if self.user else None,
            'project_name': self.project.name if self.project else None
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'assignee_id': self.assignee_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'assignee_name': self.assignee.name if self.assignee else None,
            'project_name': self.project.name if self.project else None
        }

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Self-referential relationship for threaded messages
    replies = db.relationship('Message', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def __repr__(self):
        return f'<Message {self.id} by {self.author.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'content': self.content,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'author_name': self.author.name if self.author else None,
            'project_name': self.project.name if self.project else None,
            'reply_count': self.replies.count() if self.replies else 0
        }

# Database initialization function
def init_db(app):
    """Initialize the database with the Flask app"""
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create indexes for better performance
        db.engine.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON projects(owner_id);
            CREATE INDEX IF NOT EXISTS idx_project_members_project_id ON project_members(project_id);
            CREATE INDEX IF NOT EXISTS idx_project_members_user_id ON project_members(user_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks(assignee_id);
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX IF NOT EXISTS idx_messages_project_id ON messages(project_id);
            CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
            CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_id);
            CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
        ''')
    db.init_app(app)
    with app.app_context():
        db.create_all()