#!/usr/bin/env python3
"""
REST API Example for DigitoolDB
This script demonstrates how to interact with the DigitoolDB REST API.
"""
import json
import requests
import subprocess
import sys
import time
from pathlib import Path

# Default REST API endpoint
API_URL = "http://localhost:8000"


def print_response(response, label=None):
    """Print a formatted API response"""
    if label:
        print(f"\n=== {label} ===")
    
    try:
        json_response = response.json()
        print(json.dumps(json_response, indent=2))
        return json_response
    except:
        print(f"Status: {response.status_code}")
        print(response.text)
        return None


def main():
    """Main example function"""
    print("DigitoolDB REST API Example")
    print("==========================")
    
    # Start REST API server
    print("\nStarting DigitoolDB REST API server...")
    
    # Use subprocess to start the server in background
    server_process = subprocess.Popen(
        ["python", "-m", "src.server.rest_api"],
        cwd=str(Path(__file__).parent.parent)
    )
    
    # Give the server time to start
    time.sleep(2)
    
    try:
        # Create a database
        print("\nCreating 'rest_example_db' database...")
        response = requests.post(f"{API_URL}/rest_example_db")
        print_response(response)
        
        # Create a collection
        print("\nCreating 'products' collection...")
        response = requests.post(f"{API_URL}/rest_example_db/products")
        print_response(response)
        
        # Insert documents
        print("\nInserting documents...")
        products = [
            {
                "name": "Laptop",
                "price": 999.99,
                "category": "Electronics",
                "in_stock": True
            },
            {
                "name": "Smartphone",
                "price": 699.99,
                "category": "Electronics",
                "in_stock": True
            },
            {
                "name": "Headphones",
                "price": 199.99,
                "category": "Accessories",
                "in_stock": False
            }
        ]
        
        for product in products:
            response = requests.post(
                f"{API_URL}/rest_example_db/products",
                json=product
            )
            result = print_response(response)
            print(f"Inserted {product['name']}: {result['data']['_id'] if result and result.get('success') else 'Failed'}")
        
        # Get all documents
        print("\nGetting all products...")
        response = requests.get(f"{API_URL}/rest_example_db/products")
        print_response(response, "All Products")
        
        # Get documents with filter
        print("\nGetting products in Electronics category...")
        response = requests.get(
            f"{API_URL}/rest_example_db/products?filter={json.dumps({'category': 'Electronics'})}"
        )
        print_response(response, "Electronics Products")
        
        # Update a document
        print("\nUpdating Headphones stock status...")
        response = requests.put(
            f"{API_URL}/rest_example_db/products",
            json={
                "query": {"name": "Headphones"},
                "update": {"$set": {"in_stock": True, "price": 149.99}}
            }
        )
        print_response(response)
        
        # Verify update
        print("\nVerifying Headphones update...")
        response = requests.get(
            f"{API_URL}/rest_example_db/products?filter={json.dumps({'name': 'Headphones'})}"
        )
        print_response(response, "Updated Headphones")
        
        # Delete a document
        print("\nDeleting Smartphone...")
        response = requests.delete(
            f"{API_URL}/rest_example_db/products?filter={json.dumps({'name': 'Smartphone'})}"
        )
        print_response(response)
        
        # Verify deletion
        print("\nGetting all products after deletion...")
        response = requests.get(f"{API_URL}/rest_example_db/products")
        print_response(response, "Remaining Products")
        
        # List collections
        print("\nListing collections in database...")
        response = requests.get(f"{API_URL}/rest_example_db")
        print_response(response, "Collections")
        
        # List databases
        print("\nListing all databases...")
        response = requests.get(f"{API_URL}")
        print_response(response, "Databases")
        
        # Delete the database
        print("\nDeleting test database...")
        response = requests.delete(f"{API_URL}/rest_example_db")
        print_response(response)
    
    except requests.RequestException as e:
        print(f"Error communicating with the API: {e}")
    
    finally:
        # Stop the server
        print("\nStopping REST API server...")
        server_process.terminate()
        server_process.wait()
    
    print("\nExample completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
