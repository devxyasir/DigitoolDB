"""
Data models for DigitoolDB
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Set

from .indexing import IndexManager


class Document:
    """
    Represents a document in the database.
    """
    def __init__(self, data: Dict[str, Any], doc_id: Optional[str] = None):
        """
        Initialize a document with data and optional ID.
        
        Args:
            data: The document data
            doc_id: Optional document ID, generated if not provided
        """
        self.data = data
        self.id = doc_id or str(uuid.uuid4())
        
        # Add metadata if not already present
        if '_id' not in self.data:
            self.data['_id'] = self.id
        
        if '_created_at' not in self.data:
            self.data['_created_at'] = datetime.now().isoformat()
        
        self.data['_updated_at'] = datetime.now().isoformat()

    def to_json(self) -> str:
        """
        Convert the document to a JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Document':
        """
        Create a Document from a JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            Document instance
        """
        data = json.loads(json_str)
        doc_id = data.get('_id')
        return cls(data, doc_id)


class Collection:
    """
    Represents a collection of documents.
    """
    def __init__(self, name: str, db_path: str):
        """
        Initialize a collection.
        
        Args:
            name: Collection name
            db_path: Path to the database directory
        """
        self.name = name
        self.path = os.path.join(db_path, f"{name}.digitool")
        self._ensure_collection_exists()
        
        # Initialize index manager
        self.index_manager = IndexManager(self.path)
    
    def _ensure_collection_exists(self):
        """
        Ensure the collection file exists.
        """
        if not os.path.exists(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))
        
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write('[]')
    
    def _read_collection(self) -> List[Dict[str, Any]]:
        """
        Read all documents from the collection.
        
        Returns:
            List of documents
        """
        with open(self.path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    def _write_collection(self, documents: List[Dict[str, Any]]):
        """
        Write documents to the collection.
        
        Args:
            documents: List of documents to write
        """
        with open(self.path, 'w') as f:
            json.dump(documents, f, indent=2)
    
    def create_index(self, field: str) -> bool:
        """
        Create an index on a field.
        
        Args:
            field: Field to index
            
        Returns:
            True if index was created, False if it already existed
        """
        self.index_manager.ensure_index(field)
        return True
    
    def drop_index(self, field: str) -> bool:
        """
        Drop an index.
        
        Args:
            field: Field to drop index for
            
        Returns:
            True if index was dropped, False otherwise
        """
        return self.index_manager.drop_index(field)
    
    def list_indices(self) -> List[str]:
        """
        List all indices.
        
        Returns:
            List of indexed fields
        """
        return self.index_manager.list_indices()
    
    def insert(self, document: Union[Document, Dict[str, Any]]) -> str:
        """
        Insert a document into the collection.
        
        Args:
            document: Document to insert
            
        Returns:
            Document ID
        """
        if isinstance(document, dict):
            document = Document(document)
        
        documents = self._read_collection()
        documents.append(document.data)
        self._write_collection(documents)
        
        # Update indices
        self.index_manager.add_to_indices(document.id, document.data)
        
        return document.id
    
    def find(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Find documents matching the query.
        
        Args:
            query: Query filter
            
        Returns:
            List of matching documents
        """
        documents = self._read_collection()
        
        if not query:
            return documents
        
        # Check if we can use an index for any part of the query
        indexed_doc_ids = None
        indexed_fields = self.list_indices()
        
        # Find the first indexed field in the query to use
        indexed_field = next((field for field in query if field in indexed_fields), None)
        
        if indexed_field:
            # Use the index to find matching document IDs
            indexed_doc_ids = set(self.index_manager.find_by_index(indexed_field, query[indexed_field]))
            
            # If no matches in index, we can return early
            if not indexed_doc_ids:
                return []
        
        results = []
        for doc in documents:
            # Skip documents that don't match the indexed field's results
            if indexed_doc_ids is not None and doc['_id'] not in indexed_doc_ids:
                continue
                
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            
            if match:
                results.append(doc)
        
        return results
    
    def update(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Update documents matching the query.
        
        Args:
            query: Query filter
            update: Update operations
            
        Returns:
            Number of documents updated
        """
        documents = self._read_collection()
        updated_count = 0
        
        for i, doc in enumerate(documents):
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            
            if match:
                # Save old document for index updates
                old_doc = doc.copy()
                
                # Handle MongoDB-like update operators
                if '$set' in update:
                    for k, v in update['$set'].items():
                        doc[k] = v
                elif '$inc' in update:
                    for k, v in update['$inc'].items():
                        if k in doc and isinstance(doc[k], (int, float)):
                            doc[k] += v
                        else:
                            doc[k] = v
                else:
                    # Direct update (replace)
                    # Preserve _id
                    doc_id = doc['_id']
                    doc.update(update)
                    doc['_id'] = doc_id
                
                doc['_updated_at'] = datetime.now().isoformat()
                documents[i] = doc
                updated_count += 1
                
                # Update indices
                self.index_manager.update_indices(doc['_id'], old_doc, doc)
        
        if updated_count > 0:
            self._write_collection(documents)
        
        return updated_count
    
    def delete(self, query: Dict[str, Any]) -> int:
        """
        Delete documents matching the query.
        
        Args:
            query: Query filter
            
        Returns:
            Number of documents deleted
        """
        documents = self._read_collection()
        original_count = len(documents)
        
        if not query:
            return 0
        
        new_documents = []
        deleted_docs = []
        
        for doc in documents:
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            
            if match:
                # Store for later index updates
                deleted_docs.append(doc)
            else:
                new_documents.append(doc)
        
        deleted_count = original_count - len(new_documents)
        
        if deleted_count > 0:
            self._write_collection(new_documents)
            
            # Update indices by removing deleted documents
            for doc in deleted_docs:
                self.index_manager.remove_from_indices(doc['_id'], doc)
        
        return deleted_count


class Database:
    """
    Represents a database containing collections.
    """
    def __init__(self, name: str, base_path: str):
        """
        Initialize a database.
        
        Args:
            name: Database name
            base_path: Base path for databases
        """
        self.name = name
        self.path = os.path.join(base_path, name)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """
        Ensure the database directory exists.
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
    
    def collection(self, name: str) -> Collection:
        """
        Get a collection from the database.
        
        Args:
            name: Collection name
            
        Returns:
            Collection instance
        """
        return Collection(name, self.path)
    
    def list_collections(self) -> List[str]:
        """
        List all collections in the database.
        
        Returns:
            List of collection names
        """
        collections = []
        for filename in os.listdir(self.path):
            if filename.endswith('.digitool'):
                collections.append(filename[:-9])  # Remove the .digitool extension
        
        return collections
