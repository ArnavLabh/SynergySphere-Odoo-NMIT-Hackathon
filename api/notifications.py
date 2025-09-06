from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from .models import db, Notification, Task, Project, User
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, not_found_response
from .pagination import get_pagination_params, format_pagination_response
from .utils import utc_now
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

def create_notification(user_id, type, title, message, project_id=None, task_id=None):
    """Helper function to create a notification"""
    try:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            related_project_id=project_id,
            related_task_id=task_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        db.session.rollback()
        return None

@notifications_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
@safe_db_operation("fetch notifications")
def get_notifications():
    user_id = get_jwt_identity()
    page, per_page = get_pagination_params(default_per_page=20)
    
    # Get unread count
    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    
    # Get paginated notifications
    notifications_query = Notification.query.options(
        joinedload(Notification.project),
        joinedload(Notification.task)
    ).filter_by(user_id=user_id).order_by(Notification.created_at.desc())
    
    notifications_paginated = notifications_query.paginate(page=page, per_page=per_page, error_out=False)
    
    response = format_pagination_response(notifications_paginated, 'notifications')
    response['unread_count'] = unread_count
    response['notifications'] = [{
        'id': n.id,
        'type': n.type,
        'title': n.title,
        'message': n.message,
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat(),
        'read_at': n.read_at.isoformat() if n.read_at else None,
        'project': {'id': n.project.id, 'name': n.project.name} if n.project else None,
        'task': {'id': n.task.id, 'title': n.task.title} if n.task else None
    } for n in notifications_paginated.items]
    
    return success_response(response)

@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['PATCH'])
@jwt_required()
@safe_db_operation("mark notification as read")
def mark_notification_read(notification_id):
    user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
    
    if not notification:
        return not_found_response("Notification")
    
    notification.is_read = True
    notification.read_at = utc_now()
    db.session.commit()
    
    return success_response({'message': 'Notification marked as read'})

@notifications_bp.route('/api/notifications/read-all', methods=['PATCH'])
@jwt_required()
@safe_db_operation("mark all notifications as read")
def mark_all_notifications_read():
    user_id = get_jwt_identity()
    
    Notification.query.filter_by(user_id=user_id, is_read=False).update({
        'is_read': True,
        'read_at': utc_now()
    })
    db.session.commit()
    
    return success_response({'message': 'All notifications marked as read'})

@notifications_bp.route('/api/notifications/unread-count', methods=['GET'])
@jwt_required()
@safe_db_operation("get unread notification count")
def get_unread_count():
    user_id = get_jwt_identity()
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return success_response({'unread_count': count})

# Helper functions to be called from other modules
def notify_task_assignment(task, assignee_id):
    """Send notification when a task is assigned"""
    if not assignee_id:
        return
    
    assignee = User.query.get(assignee_id)
    project = Project.query.get(task.project_id)
    
    if assignee and project:
        create_notification(
            user_id=assignee_id,
            type='task_assigned',
            title='New Task Assigned',
            message=f'You have been assigned to task "{task.title}" in project "{project.name}"',
            project_id=project.id,
            task_id=task.id
        )

def notify_task_due_soon(task):
    """Send notification when task is due soon"""
    if task.assignee_id and task.due_date:
        days_until_due = (task.due_date - utc_now()).days
        if days_until_due <= 1:
            project = Project.query.get(task.project_id)
            create_notification(
                user_id=task.assignee_id,
                type='task_due_soon',
                title='Task Due Soon',
                message=f'Task "{task.title}" in project "{project.name}" is due soon',
                project_id=project.id,
                task_id=task.id
            )

def notify_project_member_added(project_id, user_id, added_by_name):
    """Send notification when added to a project"""
    project = Project.query.get(project_id)
    if project:
        create_notification(
            user_id=user_id,
            type='project_member_added',
            title='Added to Project',
            message=f'{added_by_name} added you to project "{project.name}"',
            project_id=project_id
        )

def notify_task_status_change(task, old_status, changed_by_id):
    """Send notification when task status changes"""
    if task.assignee_id and task.assignee_id != changed_by_id:
        project = Project.query.get(task.project_id)
        changer = User.query.get(changed_by_id)
        create_notification(
            user_id=task.assignee_id,
            type='task_status_changed',
            title='Task Status Updated',
            message=f'{changer.name} changed status of "{task.title}" from {old_status} to {task.status}',
            project_id=project.id,
            task_id=task.id
        )
