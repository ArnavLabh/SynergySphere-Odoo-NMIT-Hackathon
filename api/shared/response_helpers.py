from flask import jsonify

def success_response(data=None, message=None, status=200):
    """Standard success response format"""
    response = {}
    if data is not None:
        response.update(data)
    if message:
        response['message'] = message
    return jsonify(response), status

def error_response(message, status=400):
    """Standard error response format"""
    return jsonify({'error': message}), status

def created_response(data, message="Created successfully"):
    """Standard creation response"""
    return success_response(data, message, 201)

def not_found_response(resource="Resource"):
    """Standard not found response"""
    return error_response(f"{resource} not found", 404)

def access_denied_response():
    """Standard access denied response"""
    return error_response("Access denied", 403)

def validation_error_response(fields):
    """Standard validation error response"""
    return error_response(f"Missing required fields: {', '.join(fields)}", 400)