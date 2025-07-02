"""
Simple API for DigitoolDB - A beginner-friendly wrapper around the DigitoolDB client
"""
import json
from typing import Dict, List, Any, Optional, Union

from .client import DigitoolDBClient


class SimpleDB:
    """
    A simplified wrapper for DigitoolDB that makes it easier to use
    for developers of all experience levels.
    """
    
    def __init__(self, host="localhost", port=27017, auto_connect=True):
        """
        Initialize a SimpleDB instance.
        
        Args:
            host: Server hostname (default: localhost)
            port: Server port (default: 27017)
            auto_connect: Automatically connect on initialization
        """
        self.client = DigitoolDBClient(host, port)
        self.connected = False
        
        if auto_connect:
            self.connected = self.client.connect()
    
    def __enter__(self):
        """Support for context manager (with statement)"""
        if not self.connected:
            self.connected = self.client.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting context manager"""
        self.client.disconnect()
        self.connected = False
    
    def db(self, name: str):
        """
        Get a database object for easier operations.
        
        Args:
            name: Database name
            
        Returns:
            SimplifiedDatabase object
        """
        return SimplifiedDatabase(self.client, name)
    
    def create_db(self, name: str) -> bool:
        """
        Create a new database.
        
        Args:
            name: Database name
            
        Returns:
            True if successful, False otherwise
        """
        response = self.client.create_database(name)
        return response.get('success', False)
    
    def drop_db(self, name: str) -> bool:
        """
        Delete a database.
        
        Args:
            name: Database name
            
        Returns:
            True if successful, False otherwise
        """
        response = self.client.drop_database(name)
        return response.get('success', False)
    
    def list_dbs(self) -> List[str]:
        """
        List all databases.
        
        Returns:
            List of database names
        """
        response = self.client.list_databases()
        if response.get('success', False):
            return response.get('data', [])
        return []


class SimplifiedDatabase:
    """
    A simplified wrapper for a DigitoolDB database.
    """
    
    def __init__(self, client: DigitoolDBClient, name: str):
        """
        Initialize a SimplifiedDatabase instance.
        
        Args:
            client: DigitoolDBClient instance
            name: Database name
        """
        self.client = client
        self.name = name
    
    def collection(self, name: str):
        """
        Get a collection object for easier operations.
        
        Args:
            name: Collection name
            
        Returns:
            SimplifiedCollection object
        """
        return SimplifiedCollection(self.client, self.name, name)
    
    def create_collection(self, name: str) -> bool:
        """
        Create a new collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if successful, False otherwise
        """
        response = self.client.create_collection(self.name, name)
        return response.get('success', False)
    
    def drop_collection(self, name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if successful, False otherwise
        """
        response = self.client.drop_collection(self.name, name)
        return response.get('success', False)
    
    def list_collections(self) -> List[str]:
        """
        List all collections in this database.
        
        Returns:
            List of collection names
        """
        response = self.client.list_collections(self.name)
        if response.get('success', False):
            return response.get('data', [])
        return []


class SimplifiedCollection:
    """
    A simplified wrapper for a DigitoolDB collection.
    """
    
    def __init__(self, client: DigitoolDBClient, db_name: str, name: str):
        """
        Initialize a SimplifiedCollection instance.
        
        Args:
            client: DigitoolDBClient instance
            db_name: Database name
            name: Collection name
        """
        self.client = client
        self.db_name = db_name
        self.name = name
    
    def insert(self, document: Dict[str, Any]) -> Optional[str]:
        """
        Insert a document into the collection.
        
        Args:
            document: Document to insert
            
        Returns:
            Document ID if successful, None otherwise
        """
        response = self.client.insert(self.db_name, self.name, document)
        if response.get('success', False):
            return response.get('data', {}).get('_id')
        return None
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into the collection.
        
        Args:
            documents: List of documents to insert
            
        Returns:
            List of document IDs for successfully inserted documents
        """
        ids = []
        for doc in documents:
            doc_id = self.insert(doc)
            if doc_id:
                ids.append(doc_id)
        return ids
    
    def find(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find documents matching the query.
        
        Args:
            query: Query filter (optional)
            
        Returns:
            List of matching documents
        """
        response = self.client.find(self.db_name, self.name, query or {})
        if response.get('success', False):
            return response.get('data', [])
        return []
    
    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.
        
        Args:
            query: Query filter
            
        Returns:
            Matching document or None
        """
        results = self.find(query)
        return results[0] if results else None
    
    def update(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update documents matching the query.
        
        Args:
            query: Query filter
            update: Update operations
            
        Returns:
            Number of documents updated
        """
        response = self.client.update(self.db_name, self.name, query, update)
        if response.get('success', False):
            return response.get('data', {}).get('updated_count', 0)
        return 0
    
    def delete(self, query: Dict[str, Any]) -> int:
        """
        Delete documents matching the query.
        
        Args:
            query: Query filter
            
        Returns:
            Number of documents deleted
        """
        response = self.client.delete(self.db_name, self.name, query)
        if response.get('success', False):
            return response.get('data', {}).get('deleted_count', 0)
        return 0
    
    def create_index(self, field: str) -> bool:
        """
        Create an index on a field.
        
        Args:
            field: Field to index
            
        Returns:
            True if successful, False otherwise
        """
        response = self.client.send_request({
            'action': 'create_index',
            'db_name': self.db_name,
            'collection_name': self.name,
            'field': field
        })
        return response.get('success', False)
    
    def drop_index(self, field: str) -> bool:
        """
        Drop an index.
        
        Args:
            field: Field to drop index for
            
        Returns:
            True if successful, False otherwise
        """
        response = self.client.send_request({
            'action': 'drop_index',
            'db_name': self.db_name,
            'collection_name': self.name,
            'field': field
        })
        return response.get('success', False)
    
    def list_indices(self) -> List[str]:
        """
        List all indices.
        
        Returns:
            List of indexed fields
        """
        response = self.client.send_request({
            'action': 'list_indices',
            'db_name': self.db_name,
            'collection_name': self.name
        })
        if response.get('success', False):
            return response.get('data', [])
        return []
