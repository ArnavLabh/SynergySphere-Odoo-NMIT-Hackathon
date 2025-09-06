from .models import Project, ProjectMember
from .query_utils import check_project_access_optimized

def check_project_access(project_id, user_id):
    """Check if user has access to project"""
    return check_project_access_optimized(project_id, user_id)

def require_project_access(project_id, user_id):
    """Raise exception if user doesn't have project access"""
    if not check_project_access(project_id, user_id):
        from flask import jsonify
        return jsonify({'error': 'Access denied'}), 403
    return None