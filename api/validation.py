from flask import jsonify

def validate_json(data, required_fields):
    """Validate JSON data has required fields"""
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
    
    return None