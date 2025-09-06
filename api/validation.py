from .shared.response_helpers import error_response, validation_error_response

def validate_json(data, required_fields):
    """Validate JSON data has required fields"""
    if not data:
        return error_response('No data provided')
    
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        return validation_error_response(missing)
    
    return None

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None