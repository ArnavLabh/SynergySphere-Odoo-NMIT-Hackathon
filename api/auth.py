from flask import Blueprint, request, jsonify
import bcrypt
import logging
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .models import db, User
from .validation import validate_json

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        error = validate_json(data, ['name', 'email', 'password'])
        if error:
            return error
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
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
        return jsonify({
            'token': token, 
            'user': {
                'id': user.id, 
                'name': user.name, 
                'email': user.email,
                'role': user.role
            }
        })
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database integrity error during registration: {e}")
        return jsonify({'error': 'Email already exists'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during registration: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except ValueError as e:
        logger.error(f"Validation error during registration: {e}")
        return jsonify({'error': 'Invalid input data'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error during registration: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        error = validate_json(data, ['email', 'password'])
        if error:
            return error
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = create_access_token(identity=user.id)
        return jsonify({
            'token': token, 
            'user': {
                'id': user.id, 
                'name': user.name, 
                'email': user.email,
                'role': user.role
            }
        })
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except ValueError as e:
        logger.error(f"Validation error during login: {e}")
        return jsonify({'error': 'Invalid input data'}), 400
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        return jsonify({'error': 'Login failed'}), 500