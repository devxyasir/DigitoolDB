"""
CLI interface for the DigitoolDB client
"""
import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional

from .client import DigitoolDBClient
from ..common.utils import format_response


def print_response(response: Dict[str, Any], pretty: bool = False):
    """
    Print a response from the server.
    
    Args:
        response: Response dictionary
        pretty: Whether to format the output nicely
    """
    if response.get('success'):
        if 'data' in response:
            if pretty and isinstance(response['data'], (list, dict)):
                print(json.dumps(response['data'], indent=2))
            else:
                print(response['data'])
        else:
            print("Operation successful")
    else:
        error = response.get('error', 'Unknown error')
        print(f"Error: {error}", file=sys.stderr)


def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        Path to the config file
    """
    # Check for config file in standard locations
    config_paths = [
        # First check if specified in environment
        os.environ.get('DIGITOOLDB_CONFIG'),
        # Then check standard locations
        os.path.join(os.path.expanduser('~'), '.digitooldb', 'config.json'),
        '/etc/digitooldb/config.json',
        '/etc/digid.conf',
        # Finally check current directory for development
        os.path.join(os.getcwd(), 'config', 'digid.conf')
    ]
    
    for path in config_paths:
        if path and os.path.exists(path):
            return path
    
    # Return the default path, which will use default settings if file doesn't exist
    return config_paths[1]


def main():
    """
    Main entry point for the CLI
    """
    parser = argparse.ArgumentParser(description='DigitoolDB Command Line Interface')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Common arguments for all commands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--host', help='Server hostname')
    parent_parser.add_argument('--port', type=int, help='Server port')
    parent_parser.add_argument('--config', help='Path to config file')
    parent_parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output')
    
    # Database commands
    db_parser = subparsers.add_parser('databases', parents=[parent_parser], help='List databases')
    
    create_db_parser = subparsers.add_parser('create-db', parents=[parent_parser], help='Create database')
    create_db_parser.add_argument('database', help='Database name')
    
    drop_db_parser = subparsers.add_parser('drop-db', parents=[parent_parser], help='Drop database')
    drop_db_parser.add_argument('database', help='Database name')
    
    # Collection commands
    coll_parser = subparsers.add_parser('collections', parents=[parent_parser], help='List collections')
    coll_parser.add_argument('database', help='Database name')
    
    create_coll_parser = subparsers.add_parser('create-collection', parents=[parent_parser], help='Create collection')
    create_coll_parser.add_argument('database', help='Database name')
    create_coll_parser.add_argument('collection', help='Collection name')
    
    # Document commands
    insert_parser = subparsers.add_parser('insert', parents=[parent_parser], help='Insert document')
    insert_parser.add_argument('database', help='Database name')
    insert_parser.add_argument('collection', help='Collection name')
    insert_parser.add_argument('document', help='Document to insert (JSON)')
    
    find_parser = subparsers.add_parser('find', parents=[parent_parser], help='Find documents')
    find_parser.add_argument('database', help='Database name')
    find_parser.add_argument('collection', help='Collection name')
    find_parser.add_argument('query', nargs='?', default='{}', help='Query filter (JSON)')
    
    update_parser = subparsers.add_parser('update', parents=[parent_parser], help='Update documents')
    update_parser.add_argument('database', help='Database name')
    update_parser.add_argument('collection', help='Collection name')
    update_parser.add_argument('query', help='Query filter (JSON)')
    update_parser.add_argument('update', help='Update operations (JSON)')
    
    delete_parser = subparsers.add_parser('delete', parents=[parent_parser], help='Delete documents')
    delete_parser.add_argument('database', help='Database name')
    delete_parser.add_argument('collection', help='Collection name')
    delete_parser.add_argument('query', help='Query filter (JSON)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Get config path
    config_path = args.config if args.config else get_config_path()
    
    # Create client
    client = DigitoolDBClient(config_path)
    
    # Override host/port if specified
    if args.host:
        client.config['host'] = args.host
    if args.port:
        client.config['port'] = args.port
    
    # Connect to server
    if not client.connect():
        print("Failed to connect to server", file=sys.stderr)
        return 1
    
    try:
        # Execute requested command
        if args.command == 'databases':
            response = client.list_databases()
        
        elif args.command == 'create-db':
            response = client.create_database(args.database)
        
        elif args.command == 'drop-db':
            response = client.drop_database(args.database)
        
        elif args.command == 'collections':
            response = client.list_collections(args.database)
        
        elif args.command == 'create-collection':
            response = client.create_collection(args.database, args.collection)
        
        elif args.command == 'insert':
            response = client.insert(args.database, args.collection, args.document)
        
        elif args.command == 'find':
            response = client.find(args.database, args.collection, args.query)
        
        elif args.command == 'update':
            response = client.update(args.database, args.collection, args.query, args.update)
        
        elif args.command == 'delete':
            response = client.delete(args.database, args.collection, args.query)
        
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        print_response(response, args.pretty)
        
        # Return non-zero exit code on error
        if not response.get('success'):
            return 1
    
    finally:
        # Always disconnect
        client.disconnect()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
