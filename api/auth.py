from flask import Blueprint, request
import bcrypt
from flask_jwt_extended import create_access_token
from .models import db, User
from .validation import validate_json
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, error_response, validation_error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
@safe_db_operation("user registration")
def register():
    data = request.get_json()
    
    # Enhanced validation with field-specific errors
    field_errors = {}
    
    if not data.get('name', '').strip():
        field_errors['name'] = 'Name is required'
    
    email = data.get('email', '').strip()
    if not email:
        field_errors['email'] = 'Email is required'
    elif '@' not in email or '.' not in email:
        field_errors['email'] = 'Please enter a valid email address'
    elif User.query.filter_by(email=email).first():
        field_errors['email'] = 'This email is already registered'
    
    password = data.get('password', '')
    if not password:
        field_errors['password'] = 'Password is required'
    elif len(password) < 6:
        field_errors['password'] = 'Password must be at least 6 characters long'
    
    if field_errors:
        return validation_error_response(field_errors)
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        name=data['name'].strip(),
        email=email.lower(),
        password_hash=password_hash,
        role=data.get('role', 'employee')
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = create_access_token(identity=user.id)
    return success_response({
        'token': token, 
        'user': {
            'id': user.id, 
            'name': user.name, 
            'email': user.email,
            'role': user.role
        }
    })

@auth_bp.route('/api/auth/login', methods=['POST'])
@safe_db_operation("user login")
def login():
    data = request.get_json()
    
    # Enhanced validation with field-specific errors
    field_errors = {}
    
    email = data.get('email', '').strip()
    if not email:
        field_errors['email'] = 'Email is required'
    elif '@' not in email or '.' not in email:
        field_errors['email'] = 'Please enter a valid email address'
    
    password = data.get('password', '')
    if not password:
        field_errors['password'] = 'Password is required'
    
    if field_errors:
        return validation_error_response(field_errors)
    
    user = User.query.filter_by(email=email.lower()).first()
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return error_response('Invalid email or password', 401, error_code='INVALID_CREDENTIALS')
    
    token = create_access_token(identity=user.id)
    return success_response({
        'token': token, 
        'user': {
            'id': user.id, 
            'name': user.name, 
            'email': user.email,
            'role': user.role
        }
    })