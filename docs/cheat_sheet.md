# DigitoolDB Cheat Sheet

A quick reference guide for common DigitoolDB operations.

## SimpleDB API (Recommended for Beginners)

### Connection

```python
from src.client.simple_api import SimpleDB

# Method 1: Using context manager (recommended)
with SimpleDB() as db:
    # Your code here
    pass  # Connection automatically closed

# Method 2: Manual connection
db = SimpleDB()
db.connect()
# Your code here
db.disconnect()
```

### Database Operations

```python
# Create a database
db.create_db("mydb")

# List all databases
all_dbs = db.list_dbs()

# Get a database reference
mydb = db.db("mydb")

# Drop a database
db.drop_db("mydb")
```

### Collection Operations

```python
# Create a collection
mydb.create_collection("users")

# List all collections
collections = mydb.list_collections()

# Get a collection reference
users = mydb.collection("users")

# Drop a collection
mydb.drop_collection("users")
```

### Document Operations

```python
# Insert a document
doc_id = users.insert({"name": "John", "age": 30})

# Insert multiple documents
ids = users.insert_many([
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 40}
])

# Find all documents
all_users = users.find()

# Find with query
young_users = users.find({"age": {"$lt": 30}})

# Find a single document
john = users.find_one({"name": "John"})

# Update documents
updated = users.update(
    {"name": "John"},
    {"$set": {"age": 31, "status": "active"}}
)

# Delete documents
deleted = users.delete({"status": "inactive"})
```

### Index Operations

```python
# Create an index
users.create_index("email")

# List all indices
indices = users.list_indices()

# Drop an index
users.drop_index("email")
```

## Interactive Shell

### Basic Navigation

```
# Start the shell
digi-shell

# Select a database (creates if doesn't exist)
use mydb

# Select a collection (creates if doesn't exist)
collection users

# View all databases
databases

# View collections in current database
collections

# Exit the shell
exit
```

### Document Operations

```
# Insert a document
insert {"name": "John", "age": 30}

# Find all documents
find

# Find with query
find {"age": 30}

# Update documents
update {"name": "John"} {"$set": {"age": 31}}

# Delete documents
delete {"name": "John"}
```

### Index Management

```
# Create an index
index create email

# List indices
index list

# Drop an index
index drop email
```

## Command Line Tool (digi)

### Database and Collection Management

```bash
# Create a database
digi create-db mydb

# Create a collection
digi create-collection mydb users

# List databases
digi list-dbs

# List collections
digi list-collections mydb
```

### Document Operations

```bash
# Insert a document
digi insert mydb users '{"name": "John", "age": 30}'

# Find documents (all documents)
digi find mydb users

# Find with query
digi find mydb users '{"name": "John"}'

# Update documents
digi update mydb users '{"name": "John"}' '{"$set": {"age": 31}}'

# Delete documents
digi delete mydb users '{"name": "John"}'
```

## Query Operators

```python
# Equal to
users.find({"age": 30})

# Not equal to
users.find({"age": {"$ne": 30}})

# Less than
users.find({"age": {"$lt": 30}})

# Less than or equal to
users.find({"age": {"$lte": 30}})

# Greater than
users.find({"age": {"$gt": 30}})

# Greater than or equal to
users.find({"age": {"$gte": 30}})

# In a list of values
users.find({"status": {"$in": ["active", "pending"]}})

# Not in a list of values
users.find({"status": {"$nin": ["inactive", "suspended"]}})
```

## Update Operators

```python
# Set a value
users.update({"name": "John"}, {"$set": {"age": 31}})

# Increment a value
users.update({"name": "John"}, {"$inc": {"age": 1}})

# Remove a field
users.update({"name": "John"}, {"$unset": {"temporary_field": ""}})

# Add to an array
users.update({"name": "John"}, {"$push": {"hobbies": "reading"}})

# Remove from an array
users.update({"name": "John"}, {"$pull": {"hobbies": "swimming"}})
```

## Working with Nested Fields

```python
# Insert document with nested fields
users.insert({
    "name": "John",
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "zip": "12345"
    }
})

# Query on nested field
users.find({"address.city": "Anytown"})

# Update nested field
users.update(
    {"name": "John"},
    {"$set": {"address.zip": "12346"}}
)
```

## Common Patterns

### Using with Loops

```python
with SimpleDB() as db:
    users = db.db("mydb").collection("users")
    
    # Process documents in batches
    all_users = users.find()
    for user in all_users:
        # Process each user
        print(f"Processing {user['name']}")
```

### Implementing Pagination

```python
def get_page(page_number, page_size=10):
    with SimpleDB() as db:
        users = db.db("mydb").collection("users")
        all_users = users.find()
        
        # Simple pagination
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        
        return all_users[start_idx:end_idx]
```

### Count Documents

```python
def count_documents(query=None):
    with SimpleDB() as db:
        users = db.db("mydb").collection("users")
        results = users.find(query)
        return len(results)
```

### Checking if a Document Exists

```python
def document_exists(email):
    with SimpleDB() as db:
        users = db.db("mydb").collection("users")
        user = users.find_one({"email": email})
        return user is not None
```

### Upsert (Insert if not exists, update if exists)

```python
def upsert_user(email, user_data):
    with SimpleDB() as db:
        users = db.db("mydb").collection("users")
        existing = users.find_one({"email": email})
        
        if existing:
            # Update
            users.update(
                {"email": email},
                {"$set": user_data}
            )
            return existing["_id"]
        else:
            # Insert
            user_data["email"] = email
            return users.insert(user_data)
```
