# SynergySphere API Documentation

## Base URL
- Production: `https://your-vercel-app.vercel.app`
- Local: `http://localhost:5000`

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register
- **POST** `/api/auth/register`
- Body: `{ "name": "string", "email": "string", "password": "string" }`
- Response: `{ "token": "string", "user": {...} }`

#### Login
- **POST** `/api/auth/login`
- Body: `{ "email": "string", "password": "string" }`
- Response: `{ "token": "string", "user": {...} }`

### Projects

#### Get All Projects
- **GET** `/api/projects`
- Response: `{ "projects": [...] }`

#### Get Project
- **GET** `/api/projects/{id}`
- Response: `{ "id", "name", "description", "created_at" }`

#### Create Project
- **POST** `/api/projects`
- Body: `{ "name": "string", "description": "string" }`
- Response: `{ "id", "name", "description", "created_at" }`

#### Update Project
- **PUT** `/api/projects/{id}`
- Body: `{ "name": "string", "description": "string" }`
- Response: `{ "id", "name", "description", "created_at" }`

#### Delete Project
- **DELETE** `/api/projects/{id}`
- Response: `{ "message": "Project deleted successfully" }`

### Project Members

#### Get Project Members
- **GET** `/api/projects/{id}/members`
- Response: `{ "members": [...] }`

#### Add Member
- **POST** `/api/projects/{id}/members`
- Body: `{ "email": "string", "role": "string" }`
- Response: `{ "message": "Member added successfully" }`

#### Remove Member
- **DELETE** `/api/projects/{id}/members/{member_id}`
- Response: `{ "message": "Member removed successfully" }`

### Tasks

#### Get Project Tasks
- **GET** `/api/projects/{id}/tasks`
- Response: `{ "tasks": [...], "pagination": {...} }`

#### Get My Tasks
- **GET** `/api/tasks/my-tasks`
- Response: `{ "tasks": [...], "pagination": {...} }`

#### Create Task
- **POST** `/api/projects/{id}/tasks`
- Body: `{ "title": "string", "description": "string", "assignee_id": "int", "due_date": "string", "priority": "string", "status": "string" }`
- Response: Task object

#### Update Task
- **PATCH** `/api/tasks/{id}`
- Body: Any task fields to update
- Response: Updated task object

#### Delete Task
- **DELETE** `/api/tasks/{id}`
- Response: `{ "message": "Task deleted successfully" }`

### Messages

#### Get Project Messages
- **GET** `/api/projects/{id}/messages`
- Response: `{ "messages": [...], "pagination": {...} }`

#### Send Message
- **POST** `/api/projects/{id}/messages`
- Body: `{ "content": "string", "parent_id": "int" }`
- Response: Message object

### Notifications

#### Get Notifications
- **GET** `/api/notifications`
- Response: `{ "notifications": [...], "unread_count": "int" }`

#### Mark as Read
- **PATCH** `/api/notifications/{id}/read`
- Response: `{ "message": "Notification marked as read" }`

#### Mark All as Read
- **PATCH** `/api/notifications/read-all`
- Response: `{ "message": "All notifications marked as read" }`

#### Get Unread Count
- **GET** `/api/notifications/unread-count`
- Response: `{ "unread_count": "int" }`

### Dashboard

#### Get Statistics
- **GET** `/api/dashboard/stats`
- Response: Statistics object with project counts, task counts, etc.

#### Get Recent Projects
- **GET** `/api/dashboard/recent-projects`
- Response: `{ "projects": [...] }`

#### Get Activity Timeline
- **GET** `/api/dashboard/activity-timeline?days=7`
- Response: `{ "timeline": [...] }`

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
