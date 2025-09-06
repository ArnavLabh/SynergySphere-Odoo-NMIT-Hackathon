def serialize_task(task):
    """Serialize task object to dictionary"""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'assignee_id': task.assignee_id,
        'assignee_name': task.assignee.name if task.assignee else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'priority': task.priority,
        'created_at': task.created_at.isoformat(),
        'updated_at': task.updated_at.isoformat()
    }

def serialize_message(message):
    """Serialize message object to dictionary"""
    return {
        'id': message.id,
        'content': message.content,
        'user_id': message.user_id,
        'user_name': message.user.name if message.user else 'Unknown',
        'parent_id': message.parent_id,
        'created_at': message.created_at.isoformat()
    }

def serialize_project(project):
    """Serialize project object to dictionary"""
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'owner_name': project.owner.name if hasattr(project, 'owner') and project.owner else None,
        'created_at': project.created_at.isoformat()
    }