"""
Indexing functionality for DigitoolDB
"""
import json
import os
from typing import Dict, Any, List, Set, Optional, Tuple


class Index:
    """
    Represents an index on a collection field
    """
    def __init__(self, collection_path: str, field: str):
        """
        Initialize an index.
        
        Args:
            collection_path: Path to the collection file
            field: Field to index
        """
        self.collection_path = collection_path
        self.field = field
        self.index_path = f"{collection_path}.{field}.idx"
        self.index = {}  # field_value -> [doc_ids]
        self._load_or_build_index()
    
    def _load_or_build_index(self):
        """
        Load an existing index or build a new one.
        """
        if os.path.exists(self.index_path):
            self._load_index()
        else:
            self._build_index()
    
    def _load_index(self):
        """
        Load an existing index from disk.
        """
        try:
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If index file is corrupted or missing, rebuild it
            self._build_index()
    
    def _build_index(self):
        """
        Build a new index from the collection data.
        """
        self.index = {}
        
        try:
            with open(self.collection_path, 'r') as f:
                documents = json.load(f)
            
            for document in documents:
                if self.field in document:
                    field_value = self._get_indexable_value(document[self.field])
                    doc_id = document.get('_id')
                    
                    if field_value not in self.index:
                        self.index[field_value] = []
                    
                    self.index[field_value].append(doc_id)
            
            # Save the index to disk
            self._save_index()
        
        except (json.JSONDecodeError, FileNotFoundError):
            # If collection file is corrupted or missing, initialize an empty index
            self.index = {}
    
    def _save_index(self):
        """
        Save the index to disk.
        """
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f)
    
    def _get_indexable_value(self, value: Any) -> str:
        """
        Convert a value to an indexable string key.
        
        Args:
            value: Value to convert
            
        Returns:
            String key for indexing
        """
        if isinstance(value, (dict, list)):
            # For complex types, use a JSON string
            return json.dumps(value, sort_keys=True)
        
        # For everything else, convert to string
        return str(value)
    
    def find_doc_ids(self, value: Any) -> List[str]:
        """
        Find document IDs for a specific value.
        
        Args:
            value: Value to search for
            
        Returns:
            List of matching document IDs
        """
        field_value = self._get_indexable_value(value)
        return self.index.get(field_value, [])
    
    def update(self, doc_id: str, old_value: Any, new_value: Any):
        """
        Update the index for a document.
        
        Args:
            doc_id: Document ID
            old_value: Old field value
            new_value: New field value
        """
        old_key = self._get_indexable_value(old_value) if old_value is not None else None
        new_key = self._get_indexable_value(new_value) if new_value is not None else None
        
        # Remove from old value index
        if old_key and old_key in self.index:
            if doc_id in self.index[old_key]:
                self.index[old_key].remove(doc_id)
            
            # Clean up empty index entries
            if not self.index[old_key]:
                del self.index[old_key]
        
        # Add to new value index
        if new_key:
            if new_key not in self.index:
                self.index[new_key] = []
            
            if doc_id not in self.index[new_key]:
                self.index[new_key].append(doc_id)
        
        # Save the updated index
        self._save_index()
    
    def remove(self, doc_id: str, value: Any):
        """
        Remove a document from the index.
        
        Args:
            doc_id: Document ID
            value: Field value
        """
        key = self._get_indexable_value(value) if value is not None else None
        
        if key and key in self.index:
            if doc_id in self.index[key]:
                self.index[key].remove(doc_id)
            
            # Clean up empty index entries
            if not self.index[key]:
                del self.index[key]
            
            # Save the updated index
            self._save_index()
    
    def add(self, doc_id: str, value: Any):
        """
        Add a document to the index.
        
        Args:
            doc_id: Document ID
            value: Field value
        """
        if value is None:
            return
        
        key = self._get_indexable_value(value)
        
        if key not in self.index:
            self.index[key] = []
        
        if doc_id not in self.index[key]:
            self.index[key].append(doc_id)
            
            # Save the updated index
            self._save_index()


class IndexManager:
    """
    Manages indices for a collection
    """
    def __init__(self, collection_path: str):
        """
        Initialize an index manager.
        
        Args:
            collection_path: Path to the collection file
        """
        self.collection_path = collection_path
        self.indices = {}  # field -> Index
        self._load_indices()
    
    def _load_indices(self):
        """
        Load existing indices.
        """
        # Find all index files for this collection
        collection_dir = os.path.dirname(self.collection_path)
        collection_name = os.path.basename(self.collection_path)
        
        for filename in os.listdir(collection_dir):
            if filename.startswith(collection_name) and filename.endswith('.idx'):
                # Extract field name from filename
                parts = filename.split('.')
                if len(parts) >= 3:
                    field = parts[-2]  # Format is collection_name.field.idx
                    self.indices[field] = Index(self.collection_path, field)
    
    def ensure_index(self, field: str) -> Index:
        """
        Ensure an index exists for the specified field.
        
        Args:
            field: Field to index
            
        Returns:
            Index instance
        """
        if field not in self.indices:
            self.indices[field] = Index(self.collection_path, field)
        
        return self.indices[field]
    
    def drop_index(self, field: str) -> bool:
        """
        Drop an index.
        
        Args:
            field: Field to drop index for
            
        Returns:
            True if index was dropped, False otherwise
        """
        if field in self.indices:
            index_path = f"{self.collection_path}.{field}.idx"
            
            if os.path.exists(index_path):
                os.remove(index_path)
            
            del self.indices[field]
            return True
        
        return False
    
    def list_indices(self) -> List[str]:
        """
        List all indexed fields.
        
        Returns:
            List of indexed fields
        """
        return list(self.indices.keys())
    
    def find_by_index(self, field: str, value: Any) -> List[str]:
        """
        Find document IDs by index.
        
        Args:
            field: Field to search
            value: Value to search for
            
        Returns:
            List of matching document IDs
        """
        if field in self.indices:
            return self.indices[field].find_doc_ids(value)
        
        return []
    
    def update_indices(self, doc_id: str, old_doc: Dict[str, Any], new_doc: Dict[str, Any]):
        """
        Update indices for a document.
        
        Args:
            doc_id: Document ID
            old_doc: Old document data
            new_doc: New document data
        """
        for field in self.indices:
            old_value = old_doc.get(field)
            new_value = new_doc.get(field)
            
            if old_value != new_value:
                self.indices[field].update(doc_id, old_value, new_value)
    
    def remove_from_indices(self, doc_id: str, document: Dict[str, Any]):
        """
        Remove a document from all indices.
        
        Args:
            doc_id: Document ID
            document: Document data
        """
        for field in self.indices:
            if field in document:
                self.indices[field].remove(doc_id, document[field])
    
    def add_to_indices(self, doc_id: str, document: Dict[str, Any]):
        """
        Add a document to all indices.
        
        Args:
            doc_id: Document ID
            document: Document data
        """
        for field in self.indices:
            if field in document:
                self.indices[field].add(doc_id, document[field])
