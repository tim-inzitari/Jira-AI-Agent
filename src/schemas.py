# src/schemas.py
from jsonschema import validate, ValidationError

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string", 
            "enum": ["create_issue", "find_issues"]
        },
        "project": {
            "type": "string",
            "pattern": "^[A-Z]{2,10}$"
        },
        "summary": {
            "type": "string", 
            "minLength": 5
        }
    },
    "required": ["action", "project", "summary"]
}

def validate_action(action: dict):
    try:
        validate(instance=action, schema=ACTION_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Invalid action format: {e.message}")