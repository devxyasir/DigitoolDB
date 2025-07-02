# DigitoolDB Beginner's Guide

Welcome to DigitoolDB! This guide will help you get started with this lightweight, beginner-friendly document database.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [Working with Databases and Collections](#working-with-databases-and-collections)
6. [Document Operations](#document-operations)
7. [Querying](#querying)
8. [Indexing for Performance](#indexing-for-performance)
9. [Different Ways to Use DigitoolDB](#different-ways-to-use-digitooldb)
10. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
11. [Troubleshooting](#troubleshooting)

## Introduction

DigitoolDB is a lightweight document database similar to MongoDB but much simpler and designed for local use. It's perfect for:

- Learning database concepts
- Small applications and prototypes
- Projects where you need a database but don't want the complexity of a full-scale solution

**Key Features:**
- Document-oriented storage (using JSON)
- Simple API designed for beginners
- No external dependencies
- Multiple access methods (API, CLI, REST, Interactive Shell)
- Built-in indexing for better performance

## Installation

### Prerequisites

- Python 3.6 or higher

### Installing DigitoolDB

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/digitooldb.git
   cd digitooldb
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

## Quick Start

Let's create a simple application that stores and retrieves data:

```python
from src.client.simple_api import SimpleDB

# Use the context manager to handle connections automatically
with SimpleDB() as db:
    # Create a database
    db.create_db("my_first_db")
    
    # Get a reference to the database
    my_db = db.db("my_first_db")
    
    # Create a collection (similar to a table in SQL)
    my_db.create_collection("users")
    
    # Get a reference to the collection
    users = my_db.collection("users")
    
    # Insert a document
    user_id = users.insert({
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    })
    print(f"Inserted user with ID: {user_id}")
    
    # Find the document
    john = users.find_one({"name": "John Doe"})
    print(f"Found user: {john}")
```

## Core Concepts

### Document Database vs SQL Database

Unlike traditional SQL databases that store data in tables with fixed schemas, document databases like DigitoolDB store data in flexible, JSON-like documents. This means:

- No predefined schema required
- Fields can vary from document to document
- Nested data structures are supported naturally
- Easy to modify as your application evolves

### DigitoolDB Structure

DigitoolDB organizes data in a hierarchy:

- **Server**: The running database service
- **Databases**: Containers for collections
- **Collections**: Groups of related documents (similar to tables in SQL)
- **Documents**: Individual data records stored as JSON

### Document Structure

A document is simply a JSON object. For example:

```json
{
  "_id": "abc123",
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "zip": "12345"
  },
  "hobbies": ["reading", "hiking", "coding"]
}
```

Every document automatically gets a unique `_id` field, which you can use to reference it.

## Working with Databases and Collections

### Managing Databases

```python
from src.client.simple_api import SimpleDB

with SimpleDB() as db:
    # Create a database
    db.create_db("myapp")
    
    # List all databases
    all_dbs = db.list_dbs()
    print(f"Available databases: {all_dbs}")
    
    # Get a reference to a database (creates it if it doesn't exist)
    myapp_db = db.db("myapp")
    
    # Delete a database
    db.drop_db("old_database")
```

### Managing Collections

```python
from src.client.simple_api import SimpleDB

with SimpleDB() as db:
    myapp = db.db("myapp")
    
    # Create a collection
    myapp.create_collection("products")
    
    # List all collections
    collections = myapp.list_collections()
    print(f"Collections: {collections}")
    
    # Get a reference to a collection
    products = myapp.collection("products")
    
    # Delete a collection
    myapp.drop_collection("old_collection")
```

## Document Operations

### Inserting Documents

```python
# Insert a single document
product_id = products.insert({
    "name": "Awesome Widget",
    "price": 19.99,
    "in_stock": True,
    "tags": ["gadget", "electronics"]
})

# Insert multiple documents at once
ids = products.insert_many([
    {"name": "Product A", "price": 29.99},
    {"name": "Product B", "price": 39.99}
])
```

### Finding Documents

```python
# Find all documents in a collection
all_products = products.find()

# Find with a query
cheap_products = products.find({"price": {"$lt": 25}})

# Find a single document
widget = products.find_one({"name": "Awesome Widget"})
```

### Updating Documents

```python
# Update documents matching a query
products.update(
    {"name": "Awesome Widget"},
    {"$set": {"price": 15.99, "on_sale": True}}
)

# Update all products (empty query matches everything)
products.update(
    {},
    {"$set": {"last_updated": "2025-06-03"}}
)
```

### Deleting Documents

```python
# Delete documents matching a query
products.delete({"in_stock": False})

# Delete all documents (use with caution!)
products.delete({})
```

## Querying

### Basic Queries

Find documents that exactly match a field:

```python
# Find all electronics
electronics = products.find({"category": "electronics"})

# Find products with specific price
exact_price = products.find({"price": 19.99})
```

### Query Operators

DigitoolDB supports several operators for more complex queries:

```python
# Less than
cheap = products.find({"price": {"$lt": 20}})

# Greater than
expensive = products.find({"price": {"$gt": 100}})

# Not equal
non_electronics = products.find({"category": {"$ne": "electronics"}})

# In a list of values
selected_categories = products.find({"category": {"$in": ["electronics", "gadgets"]}})
```

### Nested Fields

Query fields inside nested objects:

```python
# Find users in a specific city
california_users = users.find({"address.state": "CA"})
```

## Indexing for Performance

When your collections grow large, queries can become slow. Indexes help speed up queries:

```python
# Create an index on the 'category' field
products.create_index("category")

# Now queries that filter on category will be much faster
products.find({"category": "electronics"})

# List all indices
indices = products.list_indices()

# Remove an index when no longer needed
products.drop_index("category")
```

## Different Ways to Use DigitoolDB

### Simple API (Recommended for Beginners)

The SimpleDB API is designed to be beginner-friendly:

```python
from src.client.simple_api import SimpleDB

with SimpleDB() as db:
    # Your code here...
```

### Standard Client API

For more control, you can use the standard client API:

```python
from src.client.client import DigitoolDBClient

client = DigitoolDBClient()
client.connect()

# Operations require database and collection names every time
client.insert("mydb", "users", {"name": "John"})

client.disconnect()
```

### Interactive Shell

For quick exploration and learning, use the interactive shell:

```bash
# Start the server in one terminal
digid

# Start the interactive shell in another terminal
digi-shell
```

Then use commands like:

```
use mydb
collection users
insert {"name": "John"}
find
```

### REST API

For web applications, you can use the REST API:

```bash
# Start the REST API server
digid-rest
```

Then make HTTP requests:

```python
import requests

# Create a database
requests.post("http://localhost:5000/databases", json={"name": "mydb"})

# Insert a document
requests.post("http://localhost:5000/databases/mydb/collections/users/documents", 
              json={"name": "John"})
```

## Common Patterns and Best Practices

### Using Context Managers

Always use context managers with SimpleDB for clean connection handling:

```python
with SimpleDB() as db:
    # Your code here
    pass  # Connection is automatically closed
```

### Creating Indices Early

Create indices when you set up your database, not after it's filled with data:

```python
users = db.db("myapp").collection("users")
users.create_index("email")  # Create before adding lots of users
```

### Batch Operations

For better performance, use batch operations when possible:

```python
# Better than inserting one at a time
users.insert_many([user1, user2, user3, user4, user5])
```

### Document Design

Keep your document design sensible:

- Don't make documents too large
- Don't nest too deeply
- Keep related data together
- Use consistent field names

## Troubleshooting

### Common Errors

**Server Not Running**

If you see connection errors, make sure the server is running:

```bash
digid
```

**Invalid JSON**

If you get JSON errors, check your document format:

```python
# Valid JSON
user = {"name": "John", "age": 30}

# Invalid JSON - Python sets aren't JSON serializable
bad_user = {"name": "John", "tags": {1, 2, 3}}  # This will fail
```

**File Permission Issues**

If you get permission errors, check that your user has write access to the data directory.

### Getting Help

If you're stuck:

1. Check the examples in the `examples/` directory
2. Look at the source code - it's designed to be readable
3. Create an issue on the GitHub repository

## Next Steps

Now that you understand the basics, try:

1. Building a small application with DigitoolDB
2. Exploring the indexing system for performance
3. Trying the different interfaces (Simple API, CLI, REST)
4. Looking at the example scripts for more advanced usage
