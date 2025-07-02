# DigitoolDB Interactive Shell Guide

The DigitoolDB Interactive Shell (`digi-shell`) provides a user-friendly interface for beginners to interact with the database. This guide will help you get started quickly.

## Starting the Interactive Shell

First, make sure the DigitoolDB server is running:

```bash
digid
```

Then, in a new terminal, start the interactive shell:

```bash
digi-shell
```

You should see a welcome screen:

```
╔═══════════════════════════════════════════════╗
║           Welcome to DigitoolDB CLI           ║
║                                               ║
║    Type 'help' to see available commands      ║
║    Type 'exit' or 'quit' to exit              ║
╚═══════════════════════════════════════════════╝

DigitoolDB>
```

## Basic Commands

### Getting Help

To see all available commands:

```
DigitoolDB> help
```

For help on a specific command:

```
DigitoolDB> help find
```

### Working with Databases

List all databases:

```
DigitoolDB> databases
```

Create or use a database:

```
DigitoolDB> use mydb
```

Drop a database:

```
DigitoolDB> drop_db mydb
```

### Working with Collections

List all collections in the current database:

```
DigitoolDB/mydb> collections
```

Create or use a collection:

```
DigitoolDB/mydb> collection users
```

Drop a collection:

```
DigitoolDB/mydb> drop_collection users
```

### Working with Documents

Insert a document:

```
DigitoolDB/mydb/users> insert {"name": "John", "age": 30, "email": "john@example.com"}
```

Find all documents:

```
DigitoolDB/mydb/users> find
```

Find documents with a query:

```
DigitoolDB/mydb/users> find {"age": 30}
```

Update documents:

```
DigitoolDB/mydb/users> update {"name": "John"} {"$set": {"age": 31}}
```

Delete documents:

```
DigitoolDB/mydb/users> delete {"name": "John"}
```

### Working with Indices

Create an index for faster queries:

```
DigitoolDB/mydb/users> index create name
```

List all indices:

```
DigitoolDB/mydb/users> index list
```

Drop an index:

```
DigitoolDB/mydb/users> index drop name
```

## Example Session

Here's a complete example session:

```
DigitoolDB> use demo
Using database: demo

DigitoolDB/demo> collection products
Using collection: products

DigitoolDB/demo/products> insert {"name": "Laptop", "price": 999.99, "category": "Electronics"}
Document inserted with ID: 8f7d6e5c-4b3a-2c1d-0e9f-8a7b6c5d4e3f

DigitoolDB/demo/products> insert {"name": "Smartphone", "price": 699.99, "category": "Electronics"}
Document inserted with ID: 1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p

DigitoolDB/demo/products> find
Found 2 document(s):

--- Document 1 ---
{
  "_id": "8f7d6e5c-4b3a-2c1d-0e9f-8a7b6c5d4e3f",
  "name": "Laptop",
  "price": 999.99,
  "category": "Electronics",
  "_created_at": "2025-06-03T20:45:12.345678",
  "_updated_at": "2025-06-03T20:45:12.345678"
}

--- Document 2 ---
{
  "_id": "1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "name": "Smartphone",
  "price": 699.99,
  "category": "Electronics",
  "_created_at": "2025-06-03T20:45:23.456789",
  "_updated_at": "2025-06-03T20:45:23.456789"
}

Total: 2 document(s)

DigitoolDB/demo/products> update {"name": "Laptop"} {"$set": {"price": 899.99}}
Updated 1 document(s).

DigitoolDB/demo/products> find {"name": "Laptop"}
Found 1 document(s):

--- Document 1 ---
{
  "_id": "8f7d6e5c-4b3a-2c1d-0e9f-8a7b6c5d4e3f",
  "name": "Laptop",
  "price": 899.99,
  "category": "Electronics",
  "_created_at": "2025-06-03T20:45:12.345678",
  "_updated_at": "2025-06-03T20:46:05.678901"
}

Total: 1 document(s)

DigitoolDB/demo/products> index create category
Created index on field: category

DigitoolDB/demo/products> delete {"name": "Smartphone"}
Are you sure you want to delete matching documents? [y/N]: y
Deleted 1 document(s).

DigitoolDB/demo/products> exit
Goodbye!
```

## Tips for Beginners

1. The prompt shows your current context (database/collection)
2. Commands follow a simple noun-verb pattern
3. Use tab completion to make command entry easier
4. JSON documents don't need to be formatted - just make sure they're valid
5. Create indices on fields you search frequently for better performance

Enjoy using DigitoolDB Interactive Shell!
