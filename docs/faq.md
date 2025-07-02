# DigitoolDB Frequently Asked Questions

## General Questions

### What is DigitoolDB?
DigitoolDB is a lightweight, beginner-friendly document database implemented in Python. It's designed for local application development with no external dependencies, making it perfect for learning database concepts, building small applications, and prototyping.

### How does DigitoolDB compare to MongoDB?
DigitoolDB is inspired by MongoDB but is much simpler. Key differences:
- DigitoolDB is local-only, while MongoDB can be deployed as a distributed database
- DigitoolDB has no external dependencies, while MongoDB requires installation
- DigitoolDB's API is designed to be more beginner-friendly
- DigitoolDB lacks some advanced features of MongoDB (like aggregation pipelines and sharding)
- DigitoolDB is primarily meant for learning and small applications, not production workloads

### Is DigitoolDB suitable for production applications?
DigitoolDB is designed for learning, development, and small applications. It's not recommended for production systems with:
- High traffic loads
- Mission-critical data
- Large datasets (millions of documents)
- Distributed application needs

### What license is DigitoolDB released under?
DigitoolDB is released under the MIT license, which means you can use, modify, and distribute it freely, including for commercial purposes.

## Technical Questions

### How are documents stored in DigitoolDB?
Documents are stored as JSON files on disk. Each collection is a separate file with the extension `.json` in the configured data directory. Indices are stored in separate files with the extension `.idx`.

### Does DigitoolDB support schemas?
No, DigitoolDB is a schema-less database like most document databases. Documents in the same collection can have different fields and structure. However, this flexibility means you need to handle document validation in your application code.

### What is the maximum document size?
DigitoolDB doesn't impose a strict limit on document size, but very large documents (several MB) can impact performance since the entire collection is loaded into memory during operations. Keep documents reasonably sized for best performance.

### How many databases/collections/documents can I have?
There's no hard limit on the number of databases, collections, or documents. However, performance may degrade with:
- Very large numbers of databases/collections (thousands)
- Very large collections (hundreds of thousands of documents)
- Very large documents (multiple MB per document)

### Does DigitoolDB support transactions?
No, DigitoolDB does not support multi-document transactions. Each document operation is atomic, but you cannot group multiple operations into a single transaction that can be rolled back.

## Usage Questions

### Which API should I use as a beginner?
We recommend using the SimpleDB API (`from src.client.simple_api import SimpleDB`). It's designed specifically for beginners with:
- Context manager support for automatic connection handling
- Intuitive method names and object hierarchy
- Simplified error handling
- Chainable methods for cleaner code

### When should I create an index?
Create indices on fields that you frequently query on. For example, if you often search users by email, create an index on the email field. Indices make queries faster but slightly slow down inserts and updates. Create indices early when setting up your collections, not after they're filled with data.

### Do I need to start the server before using DigitoolDB?
Yes, you need to start the server before connecting clients. You can start it with:
```bash
digid
```
In your Python scripts, you can also start the server programmatically:
```python
from src.server.server import DigitoolDBServer
server = DigitoolDBServer()
server.start()
```

### How do I back up my data?
Since DigitoolDB stores data as JSON files, you can back up your data by copying the data directory. The default location is specified in your configuration file (`digid.conf`).

### How can I migrate data from another database to DigitoolDB?
The easiest way is to:
1. Export data from your existing database as JSON
2. Write a Python script using SimpleDB to insert the data into DigitoolDB

See the `data_analysis_example.py` for an example of importing data.

## Troubleshooting

### I can't connect to the database
Check that:
1. The server is running (`digid`)
2. You're using the correct host and port
3. There's no firewall blocking the connection
4. You haven't exceeded the maximum connections limit

### My queries are slow
Try these solutions:
1. Create indices on fields you query frequently
2. Use more specific queries to filter documents earlier
3. Check if your collections have grown very large
4. Avoid loading unnecessary data

### I'm getting a "FileNotFoundError"
This usually happens when:
1. The data directory doesn't exist
2. The user running the application doesn't have permission to write to the directory
3. You're trying to access a database or collection that doesn't exist

### Can I use DigitoolDB with web frameworks like Flask or Django?
Yes! DigitoolDB works well with any Python web framework. See the `web_dashboard_example.py` for an example using Flask.

### My documents look different when I retrieve them
DigitoolDB automatically adds some fields to your documents:
- `_id`: A unique identifier for the document
- `_created_at`: Timestamp when the document was created
- `_updated_at`: Timestamp when the document was last updated

These fields help with document management and tracking changes.

## Best Practices

### How should I structure my documents?
Follow these guidelines:
1. Keep related data together in a single document
2. Don't make documents too large (keep under 1MB if possible)
3. Use consistent field names across similar documents
4. Don't nest data too deeply (2-3 levels max for better queryability)
5. Use descriptive field names

### Should I use one large collection or many small ones?
General rule of thumb:
- Use different collections for different types of entities (users, products, orders)
- Use a single collection for entities of the same type, even if they have minor variations
- Split very large collections (millions of documents) if performance becomes an issue

### How can I optimize DigitoolDB performance?
1. Create appropriate indices for common queries
2. Keep documents reasonably sized
3. Query only the data you need
4. Batch inserts when adding multiple documents
5. Regularly clean up old or unneeded data

### What's the best way to handle relationships between documents?
Document databases like DigitoolDB handle relationships differently than SQL databases:

1. **Embedding**: For one-to-few relationships, embed related data directly in the document:
   ```json
   {
     "name": "John",
     "addresses": [
       {"type": "home", "street": "123 Main St"},
       {"type": "work", "street": "456 Market St"}
     ]
   }
   ```

2. **Referencing**: For one-to-many relationships, store references (IDs) to related documents:
   ```json
   // User document
   {
     "_id": "user123",
     "name": "John",
     "order_ids": ["order1", "order2", "order3"]
   }
   
   // Order documents
   {
     "_id": "order1",
     "user_id": "user123",
     "total": 99.99
   }
   ```

Choose based on how you'll query and update the data:
- Use embedding when related data is always accessed together and doesn't change often
- Use references when related data is accessed separately or changes frequently
