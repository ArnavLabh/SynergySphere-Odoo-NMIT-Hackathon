from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from .models import db, Project, Task, ProjectMember, User, Message, Notification
from .utils import utc_now
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
@safe_db_operation("fetch dashboard statistics")
def get_dashboard_stats():
    user_id = get_jwt_identity()
    
    # Get projects where user is owner or member
    owned_projects = Project.query.filter_by(owner_id=user_id).all()
    member_projects = db.session.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == user_id
    ).all()
    
    all_project_ids = [p.id for p in owned_projects] + [p.id for p in member_projects]
    unique_project_ids = list(set(all_project_ids))
    
    # Calculate statistics
    total_projects = len(unique_project_ids)
    
    # Task statistics
    total_tasks = Task.query.filter(Task.project_id.in_(unique_project_ids)).count() if unique_project_ids else 0
    
    my_tasks = Task.query.filter_by(assignee_id=user_id).all()
    my_total_tasks = len(my_tasks)
    my_pending_tasks = len([t for t in my_tasks if t.status != 'done'])
    my_completed_tasks = len([t for t in my_tasks if t.status == 'done'])
    
    # Tasks by status
    tasks_by_status = db.session.query(
        Task.status, func.count(Task.id)
    ).filter(
        Task.project_id.in_(unique_project_ids) if unique_project_ids else False
    ).group_by(Task.status).all()
    
    status_dict = {'todo': 0, 'in_progress': 0, 'done': 0}
    for status, count in tasks_by_status:
        status_dict[status] = count
    
    # Recent activity (last 7 days)
    week_ago = utc_now() - timedelta(days=7)
    recent_tasks = Task.query.filter(
        and_(
            Task.project_id.in_(unique_project_ids) if unique_project_ids else False,
            Task.created_at >= week_ago
        )
    ).count()
    
    recent_messages = Message.query.filter(
        and_(
            Message.project_id.in_(unique_project_ids) if unique_project_ids else False,
            Message.created_at >= week_ago
        )
    ).count()
    
    # Upcoming deadlines
    upcoming_deadlines = Task.query.filter(
        and_(
            Task.assignee_id == user_id,
            Task.due_date != None,
            Task.due_date >= utc_now(),
            Task.due_date <= utc_now() + timedelta(days=7),
            Task.status != 'done'
        )
    ).order_by(Task.due_date).limit(5).all()
    
    # Unread notifications
    unread_notifications = Notification.query.filter_by(
        user_id=user_id, 
        is_read=False
    ).count()
    
    return success_response({
        'statistics': {
            'total_projects': total_projects,
            'total_tasks': total_tasks,
            'my_tasks': {
                'total': my_total_tasks,
                'pending': my_pending_tasks,
                'completed': my_completed_tasks
            },
            'tasks_by_status': status_dict,
            'recent_activity': {
                'tasks_created': recent_tasks,
                'messages_sent': recent_messages
            },
            'unread_notifications': unread_notifications
        },
        'upcoming_deadlines': [{
            'id': task.id,
            'title': task.title,
            'project_id': task.project_id,
            'due_date': task.due_date.isoformat(),
            'priority': task.priority
        } for task in upcoming_deadlines]
    })

@dashboard_bp.route('/api/dashboard/recent-projects', methods=['GET'])
@jwt_required()
@safe_db_operation("fetch recent projects")
def get_recent_projects():
    user_id = get_jwt_identity()
    
    # Get projects with recent activity
    owned_projects = db.session.query(Project).filter_by(owner_id=user_id).all()
    member_projects = db.session.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == user_id
    ).all()
    
    all_projects = owned_projects + member_projects
    unique_projects = {p.id: p for p in all_projects}.values()
    
    # Sort by creation date and get top 6
    recent_projects = sorted(unique_projects, key=lambda x: x.created_at, reverse=True)[:6]
    
    project_data = []
    for project in recent_projects:
        task_counts = db.session.query(
            Task.status, func.count(Task.id)
        ).filter_by(project_id=project.id).group_by(Task.status).all()
        
        task_stats = {'todo': 0, 'in_progress': 0, 'done': 0}
        for status, count in task_counts:
            task_stats[status] = count
        
        member_count = ProjectMember.query.filter_by(project_id=project.id).count()
        
        project_data.append({
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'created_at': project.created_at.isoformat(),
            'task_stats': task_stats,
            'member_count': member_count + 1,  # +1 for owner
            'is_owner': project.owner_id == user_id
        })
    
    return success_response({'projects': project_data})

@dashboard_bp.route('/api/dashboard/activity-timeline', methods=['GET'])
@jwt_required()
@safe_db_operation("fetch activity timeline")
def get_activity_timeline():
    user_id = get_jwt_identity()
    days = int(request.args.get('days', 7))
    
    # Get date range
    end_date = utc_now()
    start_date = end_date - timedelta(days=days)
    
    # Get user's project IDs
    owned_projects = Project.query.filter_by(owner_id=user_id).all()
    member_projects = db.session.query(Project).join(ProjectMember).filter(
        ProjectMember.user_id == user_id
    ).all()
    
    all_project_ids = [p.id for p in owned_projects] + [p.id for p in member_projects]
    unique_project_ids = list(set(all_project_ids))
    
    if not unique_project_ids:
        return success_response({'timeline': []})
    
    # Get tasks created per day
    tasks_timeline = db.session.query(
        func.date(Task.created_at).label('date'),
        func.count(Task.id).label('count')
    ).filter(
        and_(
            Task.project_id.in_(unique_project_ids),
            Task.created_at >= start_date,
            Task.created_at <= end_date
        )
    ).group_by(func.date(Task.created_at)).all()
    
    # Convert to dictionary
    timeline_dict = {}
    for date, count in tasks_timeline:
        timeline_dict[str(date)] = count
    
    # Fill in missing dates with 0
    timeline = []
    current_date = start_date.date()
    while current_date <= end_date.date():
        timeline.append({
            'date': str(current_date),
            'tasks_created': timeline_dict.get(str(current_date), 0)
        })
        current_date += timedelta(days=1)
    
    return success_response({'timeline': timeline})
