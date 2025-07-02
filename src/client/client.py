"""
DigitoolDB Client implementation
"""
import json
import os
import socket
import sys
from typing import Dict, Any, List, Optional, Union

from ..common.utils import (
    parse_json_input,
    validate_db_name,
    validate_collection_name,
    format_response,
    get_default_config,
    load_config
)


class DigitoolDBClient:
    """
    Client class for connecting to DigitoolDB server
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the DigitoolDB client.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        self.config = get_default_config()
        if config_path and os.path.exists(config_path):
            try:
                custom_config = load_config(config_path)
                self.config.update(custom_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                print("Using default configuration")
        
        self.socket = None
    
    def connect(self) -> bool:
        """
        Connect to the DigitoolDB server.
        
        Returns:
            True if connected successfully, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.config['timeout'])
            self.socket.connect((self.config['host'], self.config['port']))
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from the DigitoolDB server.
        """
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
    
    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the server and get the response.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
            
        Raises:
            ConnectionError: If not connected to the server
        """
        if not self.socket:
            raise ConnectionError("Not connected to server")
        
        try:
            # Send request
            request_json = json.dumps(request).encode('utf-8')
            self.socket.send(request_json)
            
            # Receive response
            response_data = self.socket.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            return response
        except Exception as e:
            return format_response(False, error=f"Communication error: {e}")
    
    def list_databases(self) -> Dict[str, Any]:
        """
        List all databases.
        
        Returns:
            Response with database list
        """
        request = {
            'operation': 'list_databases'
        }
        
        return self._send_request(request)
    
    def create_database(self, db_name: str) -> Dict[str, Any]:
        """
        Create a new database.
        
        Args:
            db_name: Database name
            
        Returns:
            Response indicating success or failure
        """
        if not validate_db_name(db_name):
            return format_response(False, error="Invalid database name")
        
        request = {
            'operation': 'create_database',
            'database': db_name
        }
        
        return self._send_request(request)
    
    def drop_database(self, db_name: str) -> Dict[str, Any]:
        """
        Drop a database.
        
        Args:
            db_name: Database name
            
        Returns:
            Response indicating success or failure
        """
        request = {
            'operation': 'drop_database',
            'database': db_name
        }
        
        return self._send_request(request)
    
    def list_collections(self, db_name: str) -> Dict[str, Any]:
        """
        List collections in a database.
        
        Args:
            db_name: Database name
            
        Returns:
            Response with collection list
        """
        request = {
            'operation': 'list_collections',
            'database': db_name
        }
        
        return self._send_request(request)
    
    def create_collection(self, db_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Create a new collection in a database.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            
        Returns:
            Response indicating success or failure
        """
        if not validate_collection_name(collection_name):
            return format_response(False, error="Invalid collection name")
        
        request = {
            'operation': 'create_collection',
            'database': db_name,
            'collection': collection_name
        }
        
        return self._send_request(request)
    
    def insert(self, db_name: str, collection_name: str, 
               document: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Insert a document into a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            document: Document to insert or JSON string
            
        Returns:
            Response with document ID
        """
        # Parse document if it's a string
        if isinstance(document, str):
            try:
                document = parse_json_input(document)
            except ValueError as e:
                return format_response(False, error=str(e))
        
        request = {
            'operation': 'insert',
            'database': db_name,
            'collection': collection_name,
            'document': document
        }
        
        return self._send_request(request)
    
    def find(self, db_name: str, collection_name: str, 
             query: Union[Dict[str, Any], str, None] = None) -> Dict[str, Any]:
        """
        Find documents in a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            query: Query filter or JSON string
            
        Returns:
            Response with matching documents
        """
        # Parse query if it's a string
        if isinstance(query, str):
            try:
                query = parse_json_input(query)
            except ValueError as e:
                return format_response(False, error=str(e))
        
        # Default to empty query if None
        if query is None:
            query = {}
        
        request = {
            'operation': 'find',
            'database': db_name,
            'collection': collection_name,
            'query': query
        }
        
        return self._send_request(request)
    
    def update(self, db_name: str, collection_name: str,
               query: Union[Dict[str, Any], str], 
               update: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Update documents in a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            query: Query filter or JSON string
            update: Update operations or JSON string
            
        Returns:
            Response with count of updated documents
        """
        # Parse query and update if they're strings
        if isinstance(query, str):
            try:
                query = parse_json_input(query)
            except ValueError as e:
                return format_response(False, error=f"Invalid query: {e}")
        
        if isinstance(update, str):
            try:
                update = parse_json_input(update)
            except ValueError as e:
                return format_response(False, error=f"Invalid update: {e}")
        
        request = {
            'operation': 'update',
            'database': db_name,
            'collection': collection_name,
            'query': query,
            'update': update
        }
        
        return self._send_request(request)
    
    def delete(self, db_name: str, collection_name: str,
               query: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Delete documents from a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            query: Query filter or JSON string
            
        Returns:
            Response with count of deleted documents
        """
        # Parse query if it's a string
        if isinstance(query, str):
            try:
                query = parse_json_input(query)
            except ValueError as e:
                return format_response(False, error=f"Invalid query: {e}")
        
        request = {
            'operation': 'delete',
            'database': db_name,
            'collection': collection_name,
            'query': query
        }
        
        return self._send_request(request)
