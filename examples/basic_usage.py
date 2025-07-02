#!/usr/bin/env python3
"""
Basic usage example for DigitoolDB
This script demonstrates how to use DigitoolDB programmatically.
"""
import json
import sys
import time
from pathlib import Path

# Add the parent directory to the Python path to import the DigitoolDB modules
sys.path.append(str(Path(__file__).parent.parent))

from src.client.client import DigitoolDBClient
from src.server.server import DigitoolDBServer


def print_response(response, label=None):
    """Print a formatted response"""
    if label:
        print(f"\n=== {label} ===")
    
    if response.get('success'):
        if 'data' in response:
            print(json.dumps(response['data'], indent=2))
        else:
            print("Operation successful")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")


def main():
    """Main example function"""
    print("DigitoolDB Basic Usage Example")
    print("=============================")
    
    # Start server in background
    print("\nStarting DigitoolDB server...")
    server = DigitoolDBServer()
    
    import threading
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)
    
    # Create client and connect to server
    print("\nConnecting to server...")
    client = DigitoolDBClient()
    if not client.connect():
        print("Failed to connect to server")
        return 1
    
    try:
        # Create a database
        print("\nCreating 'example_db' database...")
        response = client.create_database('example_db')
        print_response(response)
        
        # Create a collection
        print("\nCreating 'users' collection...")
        response = client.create_collection('example_db', 'users')
        print_response(response)
        
        # Insert documents
        print("\nInserting documents...")
        users = [
            {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'},
            {'name': 'Bob', 'age': 25, 'email': 'bob@example.com'},
            {'name': 'Charlie', 'age': 35, 'email': 'charlie@example.com'}
        ]
        
        for user in users:
            response = client.insert('example_db', 'users', user)
            print(f"Inserted {user['name']}: {response['data']['_id'] if response['success'] else 'Failed'}")
        
        # Find all documents
        response = client.find('example_db', 'users')
        print_response(response, "All Users")
        
        # Find with query
        response = client.find('example_db', 'users', {'age': 25})
        print_response(response, "Users aged 25")
        
        # Update a document
        print("\nUpdating Bob's age to 26...")
        response = client.update(
            'example_db', 'users',
            {'name': 'Bob'},
            {'$set': {'age': 26}}
        )
        print(f"Updated {response['data']['updated_count'] if response['success'] else 0} document(s)")
        
        # Verify update
        response = client.find('example_db', 'users', {'name': 'Bob'})
        print_response(response, "Bob's updated document")
        
        # Delete a document
        print("\nDeleting Charlie's document...")
        response = client.delete('example_db', 'users', {'name': 'Charlie'})
        print(f"Deleted {response['data']['deleted_count'] if response['success'] else 0} document(s)")
        
        # Verify deletion
        response = client.find('example_db', 'users')
        print_response(response, "Remaining users")
        
        # Clean up
        print("\nDropping example_db...")
        response = client.drop_database('example_db')
        print_response(response)
    
    finally:
        # Disconnect client
        client.disconnect()
        
        # Stop server
        print("\nStopping server...")
        server.stop()
    
    print("\nExample completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
