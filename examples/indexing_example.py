#!/usr/bin/env python3
"""
Indexing Example for DigitoolDB
This script demonstrates how to use the indexing functionality to improve query performance.
"""
import json
import sys
import time
import random
from pathlib import Path
from datetime import datetime

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


def performance_test(client, db_name, collection_name, field, query_value, iterations=5):
    """Test query performance with and without an index"""
    times = {'without_index': [], 'with_index': []}

    # Query without index
    print(f"\nTesting query performance WITHOUT index on '{field}'...")
    for i in range(iterations):
        start_time = time.time()
        response = client.find(db_name, collection_name, {field: query_value})
        end_time = time.time()
        times['without_index'].append(end_time - start_time)
        print(f"  Query {i+1}: {times['without_index'][-1]:.6f} seconds")
    
    # Create index
    print(f"\nCreating index on '{field}'...")
    response = client.send_request({
        'action': 'create_index',
        'db_name': db_name,
        'collection_name': collection_name,
        'field': field
    })
    print_response(response)
    
    # Query with index
    print(f"\nTesting query performance WITH index on '{field}'...")
    for i in range(iterations):
        start_time = time.time()
        response = client.find(db_name, collection_name, {field: query_value})
        end_time = time.time()
        times['with_index'].append(end_time - start_time)
        print(f"  Query {i+1}: {times['with_index'][-1]:.6f} seconds")
    
    # Show performance comparison
    avg_without = sum(times['without_index']) / len(times['without_index'])
    avg_with = sum(times['with_index']) / len(times['with_index'])
    improvement = ((avg_without - avg_with) / avg_without) * 100 if avg_without > 0 else 0
    
    print("\n=== Performance Comparison ===")
    print(f"Average query time WITHOUT index: {avg_without:.6f} seconds")
    print(f"Average query time WITH index: {avg_with:.6f} seconds")
    print(f"Performance improvement: {improvement:.2f}%")
    
    return times


def main():
    """Main example function"""
    print("DigitoolDB Indexing Example")
    print("===========================")
    
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
        db_name = "index_example_db"
        collection_name = "users"
        
        # Create a database
        print(f"\nCreating '{db_name}' database...")
        response = client.create_database(db_name)
        print_response(response)
        
        # Create a collection
        print(f"\nCreating '{collection_name}' collection...")
        response = client.create_collection(db_name, collection_name)
        print_response(response)
        
        # Insert test data (1000 users)
        print("\nInserting 1000 test users...")
        domains = ["example.com", "test.com", "digitool.com", "email.com", "demo.com"]
        cities = ["New York", "London", "Tokyo", "Paris", "Berlin", "Sydney", "Toronto", "Singapore"]
        
        for i in range(1000):
            user = {
                "username": f"user{i}",
                "email": f"user{i}@{random.choice(domains)}",
                "age": random.randint(18, 70),
                "city": random.choice(cities),
                "active": random.choice([True, False]),
                "created_at": datetime.now().isoformat()
            }
            response = client.insert(db_name, collection_name, user)
            if i % 100 == 0:
                print(f"  Inserted {i} users...")
        
        print("All users inserted successfully")
        
        # Test query performance by city (non-unique field)
        target_city = "London"
        print(f"\nTesting query performance for city='{target_city}'")
        city_times = performance_test(client, db_name, collection_name, "city", target_city)
        
        # List available indices
        print("\nListing available indices...")
        response = client.send_request({
            'action': 'list_indices',
            'db_name': db_name,
            'collection_name': collection_name
        })
        print_response(response, "Available Indices")
        
        # Test query performance by username (unique field)
        target_username = "user500"
        print(f"\nTesting query performance for username='{target_username}'")
        username_times = performance_test(client, db_name, collection_name, "username", target_username)
        
        # Drop an index
        print("\nDropping city index...")
        response = client.send_request({
            'action': 'drop_index',
            'db_name': db_name,
            'collection_name': collection_name,
            'field': "city"
        })
        print_response(response)
        
        # List available indices
        print("\nListing available indices after dropping city index...")
        response = client.send_request({
            'action': 'list_indices',
            'db_name': db_name,
            'collection_name': collection_name
        })
        print_response(response, "Available Indices")
        
        # Clean up
        print("\nDropping example database...")
        response = client.drop_database(db_name)
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
