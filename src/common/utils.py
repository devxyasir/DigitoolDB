"""
Utility functions for DigitoolDB
"""
import json
import os
import re
from typing import Dict, Any, List, Optional, Union


def parse_json_input(json_str: str) -> Dict[str, Any]:
    """
    Parse a JSON string input, with error handling.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed JSON object
        
    Raises:
        ValueError: If the JSON is invalid
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def validate_db_name(name: str) -> bool:
    """
    Validate a database name.
    
    Args:
        name: Database name to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Alphanumeric and underscore only, non-empty
    return bool(re.match(r'^[a-zA-Z0-9_]+$', name))


def validate_collection_name(name: str) -> bool:
    """
    Validate a collection name.
    
    Args:
        name: Collection name to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Alphanumeric and underscore only, non-empty
    return bool(re.match(r'^[a-zA-Z0-9_]+$', name))


def format_response(success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
    """
    Format a standard response object.
    
    Args:
        success: Whether the operation was successful
        data: Optional data to include
        error: Optional error message
        
    Returns:
        Formatted response dictionary
    """
    response = {
        'success': success
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    return response


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If the config file doesn't exist
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return json.load(f)


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration values.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'host': '127.0.0.1',
        'port': 27017,  # MongoDB-like default port
        'data_dir': os.path.join(os.path.expanduser('~'), '.digitooldb', 'data'),
        'log_level': 'info',
        'log_file': os.path.join(os.path.expanduser('~'), '.digitooldb', 'logs', 'digitooldb.log'),
        'auth_enabled': False,
        'max_connections': 100,
        'timeout': 30  # seconds
    }


def ensure_dir_exists(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def list_databases(base_path: str) -> List[str]:
    """
    List all databases in the specified base path.
    
    Args:
        base_path: Base path for databases
        
    Returns:
        List of database names
    """
    if not os.path.exists(base_path):
        return []
    
    return [name for name in os.listdir(base_path) 
            if os.path.isdir(os.path.join(base_path, name))]
