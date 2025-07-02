#!/usr/bin/env python3
"""
Simple API Example for DigitoolDB
This script demonstrates how to use the beginner-friendly Simple API.
"""
import sys
import time
from pathlib import Path

# Add the parent directory to the Python path to import the DigitoolDB modules
sys.path.append(str(Path(__file__).parent.parent))

from src.client.simple_api import SimpleDB
from src.server.server import DigitoolDBServer


def main():
    """Main example function"""
    print("DigitoolDB Simple API Example")
    print("============================")
    
    # Start server in background
    print("\nStarting DigitoolDB server...")
    server = DigitoolDBServer()
    
    import threading
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)
    
    # Connect to database using context manager (automatically handles connection/disconnection)
    print("\nConnecting to the database...")
    
    with SimpleDB() as db:
        # Create a database
        print("\n1. Creating a database")
        db.create_db("simple_example")
        
        # Get a handle to the database
        simple_db = db.db("simple_example")
        
        # Create a collection
        print("\n2. Creating a collection")
        simple_db.create_collection("products")
        
        # Get a handle to the collection
        products = simple_db.collection("products")
        
        # Create an index for faster queries
        print("\n3. Creating an index on 'category' field")
        products.create_index("category")
        
        # Insert documents
        print("\n4. Inserting documents")
        products.insert({"name": "Laptop", "price": 999.99, "category": "Electronics"})
        products.insert({"name": "Headphones", "price": 99.99, "category": "Electronics"})
        products.insert({"name": "Coffee Mug", "price": 12.99, "category": "Kitchen"})
        
        # Insert multiple documents at once
        print("\n5. Inserting multiple documents at once")
        books = [
            {"name": "Python Programming", "price": 45.99, "category": "Books"},
            {"name": "Database Design", "price": 39.99, "category": "Books"}
        ]
        ids = products.insert_many(books)
        print(f"   Inserted {len(ids)} books with IDs: {ids}")
        
        # Find all documents
        print("\n6. Finding all products")
        all_products = products.find()
        print(f"   Found {len(all_products)} products:")
        for product in all_products:
            print(f"   - {product['name']}: ${product['price']} ({product['category']})")
        
        # Find documents by query
        print("\n7. Finding products in the Electronics category")
        electronics = products.find({"category": "Electronics"})
        print(f"   Found {len(electronics)} electronics products:")
        for product in electronics:
            print(f"   - {product['name']}: ${product['price']}")
        
        # Find a single document
        print("\n8. Finding a single product")
        laptop = products.find_one({"name": "Laptop"})
        if laptop:
            print(f"   Found laptop: ${laptop['price']}")
        
        # Update documents
        print("\n9. Updating the laptop price")
        updated = products.update(
            {"name": "Laptop"}, 
            {"$set": {"price": 899.99, "on_sale": True}}
        )
        print(f"   Updated {updated} document(s)")
        
        # Verify the update
        laptop = products.find_one({"name": "Laptop"})
        print(f"   Laptop now: ${laptop['price']} (on sale: {laptop.get('on_sale', False)})")
        
        # Delete documents
        print("\n10. Deleting a product")
        deleted = products.delete({"name": "Coffee Mug"})
        print(f"   Deleted {deleted} document(s)")
        
        # List collections
        print("\n11. Listing collections")
        collections = simple_db.list_collections()
        print(f"   Collections in database: {collections}")
        
        # List indices
        print("\n12. Listing indices")
        indices = products.list_indices()
        print(f"   Indices on products collection: {indices}")
        
        # Cleanup
        print("\n13. Cleaning up")
        db.drop_db("simple_example")
        print("   Database dropped")
    
    # Stop the server
    print("\nStopping server...")
    server.stop()
    
    print("\nExample completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
