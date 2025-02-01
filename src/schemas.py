from jsonschema import validate, ValidationError

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string", 
            "enum": ["create_issue"]
        },
        "project": {
            "type": "string",
            "pattern": "^[A-Z]{2,10}$"
        },
        "summary": {
            "type": "string", 
            "minLength": 5,
            "maxLength": 255
        },
        "description": {
            "type": "string",
            "maxLength": 2000
        }
    },
    "required": ["action", "project", "summary"],
    "additionalProperties": True
}

def validate_action(action: dict):
    try:
        validate(instance=action, schema=ACTION_SCHEMA)
    except ValidationError as e:
        # Add detailed error message
        error_path = ".".join(str(v) for v in e.absolute_path)
        error_msg = f"Validation failed for field '{error_path}': {e.message}"
        raise ValueError(error_msg) from None