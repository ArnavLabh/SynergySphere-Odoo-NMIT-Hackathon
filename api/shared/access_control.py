from functools import wraps
from flask_jwt_extended import get_jwt_identity
from .response_helpers import access_denied_response
from ..permissions import check_project_access

def require_project_member(project_id_param='project_id'):
    """Decorator to ensure user has project access"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            project_id = kwargs.get(project_id_param)
            
            if not check_project_access(project_id, user_id):
                return access_denied_response()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator