from flask import Blueprint, request, jsonify
import bcrypt
from flask_jwt_extended import create_access_token
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=password_hash.decode('utf-8')
    )
    
    db.session.add(user)
    db.session.commit()
    
    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email}})

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = create_access_token(identity=user.id)
    return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'email': user.email}})