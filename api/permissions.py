from .models import Project, ProjectMember
from .query_utils import check_project_access_optimized
from .shared.response_helpers import access_denied_response

def check_project_access(project_id, user_id):
    """Check if user has access to project"""
    return check_project_access_optimized(project_id, user_id)

def require_project_access(project_id, user_id):
    """Return error response if user doesn't have project access"""
    if not check_project_access(project_id, user_id):
        return access_denied_response()
    return None

def check_project_ownership(project_id, user_id):
    """Check if user owns the project"""
    project = Project.query.get(project_id)
    return project and project.owner_id == user_id