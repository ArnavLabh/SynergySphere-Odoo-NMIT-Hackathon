from flask import Blueprint, request
import bcrypt
from flask_jwt_extended import create_access_token
from .models import db, User
from .validation import validate_json
from .shared.db_operations import safe_db_operation
from .shared.response_helpers import success_response, error_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
@safe_db_operation("user registration")
def register():
    data = request.get_json()
    
    error = validate_json(data, ['name', 'email', 'password'])
    if error:
        return error
    
    if User.query.filter_by(email=data['email']).first():
        return error_response('Email already exists')
    
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        name=data['name'],
        email=data['email'],
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
    
    error = validate_json(data, ['email', 'password'])
    if error:
        return error
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return error_response('Invalid credentials', 401)
    
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