# DigitoolDB

A lightweight, beginner-friendly, document-oriented NoSQL database implemented in Python.

## Overview

DigitoolDB is a simplified NoSQL database system designed for local use, providing a MongoDB-like interface for storing and querying JSON documents. It's built with simplicity in mind, having no external dependencies and providing both a programmatic API and command-line interface.

### Key Features

- **Super Simple API**: Beginner-friendly syntax that anyone can use
- **No External Dependencies**: Works with Python standard library only
- **Multiple Access Methods**: Programming API, CLI tool, and REST interface
- **Performance Optimized**: Built-in indexing for faster queries
- **Local-Only**: Designed for local application development
- Uses a MongoDB-like structure with collections and databases
- Runs as a local daemon or server process
- Provides a CLI tool (`digi`) for interacting with the database

## Components

- **digid**: The database server process
- **digi**: Command-line interface for interacting with the database

## Directory Structure

```
DigitoolDB/
├── src/
│   ├── server/      # digid server implementation
│   ├── client/      # digi CLI implementation
│   └── common/      # shared code
├── config/          # configuration files
├── data/            # where database files will be stored
├── tests/           # unit tests
├── docs/            # documentation
└── scripts/         # install scripts
```

## Installation

1. Ensure Python 3.8+ is installed
2. Clone this repository
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run setup:
   ```
   python setup.py install
   ```

## Usage

### Simple API (Recommended for Beginners)

```python
from src.client.simple_api import SimpleDB

# Use with a context manager - handles connections automatically
with SimpleDB() as db:
    # Create a database
    db.create_db('mydb')
    
    # Get a database reference
    mydb = db.db('mydb')
    
    # Create a collection
    mydb.create_collection('users')
    
    # Get a collection reference
    users = mydb.collection('users')
    
    # Insert a document
    users.insert({'name': 'John', 'age': 30})
    
    # Find documents
    results = users.find({'name': 'John'})
    print(results)
    
    # Find a single document
    john = users.find_one({'name': 'John'})
    
    # Update documents
    users.update({'name': 'John'}, {'$set': {'age': 31}})
    
    # Delete documents
    users.delete({'name': 'John'})
```

### Standard Programmatic API

```python
from src.client.client import DigitoolDBClient

# Connect to the server
client = DigitoolDBClient()
client.connect()

# Create a database and collection
client.create_database('mydb')
client.create_collection('mydb', 'users')

# Insert a document
client.insert('mydb', 'users', {'name': 'John', 'age': 30})

# Find documents
results = client.find('mydb', 'users', {'name': 'John'})
print(results)

# Update documents
client.update('mydb', 'users', {'name': 'John'}, {'$set': {'age': 31}})

# Delete documents
client.delete('mydb', 'users', {'name': 'John'})

# Disconnect when done
client.disconnect()
```

### Starting the server

```
digid --config /path/to/config.json
```

### Using the CLI

```
# Insert a document
digi insert users '{"name": "Yasir"}'

# Find documents
digi find users '{"name": "Yasir"}'

# Update documents
digi update users '{"name": "Yasir"}' '{"$set": {"age": 30}}'

# Delete documents
digi delete users '{"name": "Yasir"}'
```

## Configuration

The default configuration file is located at `/etc/digid.conf` (or `config/digid.conf` in development). You can specify:

- Data storage directory
- Server port
- Log level and location

## Documentation

DigitoolDB provides comprehensive documentation to help users get started:

- [Getting Started Guide](./docs/getting_started.md): Step-by-step instructions for installation and first use
- [Beginner's Guide](./docs/beginners_guide.md): Detailed information for beginners
- [Cheat Sheet](./docs/cheat_sheet.md): Quick reference for common operations
- [FAQ](./docs/faq.md): Answers to frequently asked questions

## Examples

The following examples are available to demonstrate various use cases:

- [Simple API Example](./examples/simple_api_example.py): Basic operations using the SimpleDB API
- [Todo App Example](./examples/todo_app_example.py): A complete Todo application
- [Data Analysis Example](./examples/data_analysis_example.py): Using DigitoolDB for data analysis
- [Web Dashboard Example](./examples/web_dashboard_example.py): Interactive web interface for DigitoolDB

## License

MIT License
