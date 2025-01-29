"""Request validation utilities."""

from typing import Dict, Any
from werkzeug.exceptions import BadRequest
from flask import Request

def validate_request_data(request: Request, schema: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Validate request data against a schema.
    
    Args:
        request: Flask request object
        schema: Validation schema
            Example:
            {
                'name': {'type': str, 'required': True},
                'age': {'type': int, 'required': False}
            }
            
    Returns:
        Validated data
        
    Raises:
        BadRequest: If validation fails
    """
    data = request.get_json()
    if not data:
        raise BadRequest("Missing request body")
        
    validated = {}
    for field, rules in schema.items():
        value = data.get(field)
        
        if rules.get('required', False) and value is None:
            raise BadRequest(f"Missing required field: {field}")
            
        if value is not None:
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                raise BadRequest(f"Invalid type for {field}. Expected {expected_type.__name__}")
                
            validated[field] = value
            
    return validated
