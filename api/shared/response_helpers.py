from flask import jsonify

def success_response(data=None, message=None, status=200):
    """Standard success response format"""
    response = {'success': True}
    if data is not None:
        response.update(data)
    if message:
        response['message'] = message
    return jsonify(response), status

def error_response(message, status=400, field_errors=None, error_code=None):
    """Enhanced error response format with field-specific errors"""
    response = {
        'success': False,
        'error': message
    }
    if field_errors:
        response['field_errors'] = field_errors
    if error_code:
        response['error_code'] = error_code
    return jsonify(response), status

def validation_error_response(field_errors, message="Validation failed"):
    """Validation error with field-specific messages"""
    return error_response(message, 400, field_errors, 'VALIDATION_ERROR')

def created_response(data, message="Created successfully"):
    """Standard creation response"""
    return success_response(data, message, 201)

def not_found_response(resource="Resource"):
    """Standard not found response"""
    return error_response(f"{resource} not found", 404, error_code='NOT_FOUND')

def access_denied_response():
    """Standard access denied response"""
    return error_response("Access denied", 403, error_code='ACCESS_DENIED')