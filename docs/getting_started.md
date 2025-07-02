# Getting Started with DigitoolDB

This guide will walk you through the process of installing, configuring, and getting started with DigitoolDB. By the end, you'll have a working database and understand how to perform basic operations.

## Prerequisites

Before you begin, make sure you have:

- Python 3.6 or higher installed
- Basic familiarity with command-line operations
- A text editor or IDE of your choice

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/digitooldb.git
cd digitooldb
```

### Step 2: Install DigitoolDB

Install the package in development mode:

```bash
pip install -e .
```

This makes the `digid` and `digi-shell` commands available in your terminal.

## Starting the Database Server

### Step 1: Start the Server

To start the DigitoolDB server:

```bash
digid
```

You should see output indicating that the server is running:

```
Starting DigitoolDB server on localhost:27017...
Server started successfully!
```

The server runs in the foreground by default. To run it in the background, you can use:

```bash
# On Linux/Mac
digid &

# On Windows
start digid
```

## Your First Database

### Method 1: Using the Interactive Shell (Recommended for Beginners)

The interactive shell provides a user-friendly interface for working with DigitoolDB:

```bash
digi-shell
```

You'll see a welcome screen:

```
╔═══════════════════════════════════════════════╗
║           Welcome to DigitoolDB CLI           ║
║                                               ║
║    Type 'help' to see available commands      ║
║    Type 'exit' or 'quit' to exit              ║
╚═══════════════════════════════════════════════╝

DigitoolDB>
```

Create your first database:

```
DigitoolDB> use mydb
Using database: mydb

DigitoolDB/mydb> collection users
Using collection: users

DigitoolDB/mydb/users> insert {"name": "John", "age": 30}
Document inserted with ID: abc123def456

DigitoolDB/mydb/users> find
Found 1 document(s):

--- Document 1 ---
{
  "_id": "abc123def456",
  "name": "John",
  "age": 30,
  "_created_at": "2025-06-04T10:58:12.345678",
  "_updated_at": "2025-06-04T10:58:12.345678"
}

Total: 1 document(s)
```

### Method 2: Using the Simple API in Python

Create a new Python file (e.g., `first_db.py`) with the following code:

```python
from src.client.simple_api import SimpleDB

# Connect to database using context manager
with SimpleDB() as db:
    # Create a database
    db.create_db("mydb")
    
    # Get a database reference
    mydb = db.db("mydb")
    
    # Create a collection
    mydb.create_collection("users")
    
    # Get a collection reference
    users = mydb.collection("users")
    
    # Insert a document
    user_id = users.insert({"name": "John", "age": 30})
    print(f"Inserted user with ID: {user_id}")
    
    # Find all documents
    all_users = users.find()
    print("All users:")
    for user in all_users:
        print(f"- {user['name']}, {user['age']} years old")
```

Run your script:

```bash
python first_db.py
```

## Common Operations

### Creating and Managing Databases

```python
with SimpleDB() as db:
    # Create a database
    db.create_db("mydb")
    
    # List all databases
    all_dbs = db.list_dbs()
    print(f"All databases: {all_dbs}")
    
    # Delete a database
    db.drop_db("old_db")
```

### Working with Collections

```python
with SimpleDB() as db:
    mydb = db.db("mydb")
    
    # Create a collection
    mydb.create_collection("products")
    
    # List all collections
    collections = mydb.list_collections()
    print(f"Collections: {collections}")
    
    # Delete a collection
    mydb.drop_collection("temp")
```

### Document Operations

```python
with SimpleDB() as db:
    products = db.db("mydb").collection("products")
    
    # Insert a document
    product_id = products.insert({
        "name": "Laptop", 
        "price": 999.99,
        "in_stock": True
    })
    
    # Find documents
    laptops = products.find({"name": "Laptop"})
    
    # Update documents
    products.update(
        {"name": "Laptop"},
        {"$set": {"price": 899.99, "on_sale": True}}
    )
    
    # Delete documents
    products.delete({"in_stock": False})
```

## Using the Command-Line Interface

DigitoolDB comes with a command-line tool (`digi`) for quick operations:

```bash
# Create a database
digi create-db mydb

# Create a collection
digi create-collection mydb users

# Insert a document (as JSON string)
digi insert mydb users '{"name": "John", "age": 30}'

# Find documents
digi find mydb users

# Find with a query
digi find mydb users '{"name": "John"}'

# Update documents
digi update mydb users '{"name": "John"}' '{"$set": {"age": 31}}'

# Delete documents
digi delete mydb users '{"name": "John"}'
```

## Configuration

### Customizing Server Settings

DigitoolDB uses a configuration file (`digid.conf`) to control server behavior. By default, this file is located at:

- `/etc/digid.conf` on Linux/Mac
- `C:\ProgramData\DigitoolDB\digid.conf` on Windows

If you installed DigitoolDB from the repository, a sample configuration file is located at `config/digid.conf`.

Example configuration:

```json
{
  "host": "localhost",
  "port": 27017,
  "data_dir": "/var/lib/digitooldb",
  "log_file": "/var/log/digitooldb/server.log",
  "log_level": "INFO",
  "max_connections": 10
}
```

To use a custom configuration file:

```bash
digid --config /path/to/your/digid.conf
```

## Troubleshooting

### Connection Issues

If you get connection errors like:

```
Could not connect to DigitoolDB server at localhost:27017
```

Check that:

1. The server is running (start it with `digid`)
2. You're using the correct host and port
3. No firewall is blocking the connection
4. The maximum connections limit hasn't been reached

### Permission Errors

If you see file permission errors:

```
Permission denied: '/var/lib/digitooldb/mydb'
```

Ensure that:

1. Your user has write access to the data directory
2. If using a custom data directory, it exists and has the correct permissions

### JSON Errors

If you get JSON-related errors:

```
Error: Invalid JSON document
```

Make sure your JSON is valid. Common issues include:

- Missing or extra commas
- Unquoted property names
- Single quotes instead of double quotes
- Using Python-specific data types that aren't valid JSON (like sets)

## Next Steps

Now that you have DigitoolDB up and running, you can:

1. Try the [examples in the repository](../examples/) to see more advanced usage
2. Read the [Beginner's Guide](./beginners_guide.md) for a deeper understanding
3. Experiment with the interactive shell using `digi-shell`
4. Start building your own applications with DigitoolDB!
