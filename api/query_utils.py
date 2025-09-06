from sqlalchemy.orm import joinedload
from .models import db, Project, ProjectMember

def get_user_projects_query(user_id):
    """Optimized query to get projects for a user (owned or member)"""
    return db.session.query(Project).options(joinedload(Project.owner)).filter(
        db.or_(
            Project.owner_id == user_id,
            Project.id.in_(
                db.session.query(ProjectMember.project_id).filter(ProjectMember.user_id == user_id)
            )
        )
    ).distinct()

def check_project_access_optimized(project_id, user_id):
    """Optimized project access check with single query"""
    return db.session.query(
        db.exists().where(
            db.or_(
                db.and_(Project.id == project_id, Project.owner_id == user_id),
                db.and_(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id
                )
            )
        )
    ).scalar()