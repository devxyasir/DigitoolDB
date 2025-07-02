"""
DigitoolDB Server implementation
"""
import json
import logging
import os
import socket
import threading
import time
from typing import Dict, Any, List, Optional, Tuple, Union

from ..common.models import Database, Collection, Document
from ..common.utils import (
    parse_json_input, 
    format_response, 
    get_default_config, 
    load_config,
    ensure_dir_exists,
    list_databases
)


class DigitoolDBServer:
    """
    Main server class for DigitoolDB
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the DigitoolDB server.
        
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
        
        # Setup logging
        self._setup_logging()
        
        # Ensure data directory exists
        ensure_dir_exists(self.config['data_dir'])
        
        # Initialize server socket
        self.server_socket = None
        self.running = False
        self.clients = []
        
        # Cache for open databases
        self.db_cache = {}
        
        self.logger.info("DigitoolDB Server initialized")
    
    def _setup_logging(self):
        """
        Set up logging for the server.
        """
        log_dir = os.path.dirname(self.config['log_file'])
        ensure_dir_exists(log_dir)
        
        logging.basicConfig(
            level=getattr(logging, self.config['log_level'].upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file']),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('digid')
    
    def start(self):
        """
        Start the DigitoolDB server.
        """
        if self.running:
            self.logger.warning("Server is already running")
            return
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config['host'], self.config['port']))
            self.server_socket.listen(self.config['max_connections'])
            
            self.running = True
            self.logger.info(f"Server started on {self.config['host']}:{self.config['port']}")
            
            # Start connection handler in a separate thread
            self.accept_thread = threading.Thread(target=self._accept_connections)
            self.accept_thread.daemon = True
            self.accept_thread.start()
            
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            self.running = False
    
    def stop(self):
        """
        Stop the DigitoolDB server.
        """
        self.logger.info("Stopping server...")
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        self.logger.info("Server stopped")
    
    def _accept_connections(self):
        """
        Accept incoming client connections.
        """
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_socket.settimeout(self.config['timeout'])
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                self.clients.append(client_socket)
                self.logger.info(f"New connection from {address[0]}:{address[1]}")
            
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting connection: {e}")
                    time.sleep(1)
    
    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """
        Handle communication with a connected client.
        
        Args:
            client_socket: Client socket
            address: Client address
        """
        try:
            while self.running:
                # Receive data from client
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Process the request
                try:
                    request = json.loads(data.decode('utf-8'))
                    response = self._process_request(request)
                except json.JSONDecodeError:
                    response = format_response(False, error="Invalid JSON request")
                except Exception as e:
                    self.logger.error(f"Error processing request: {e}")
                    response = format_response(False, error=str(e))
                
                # Send response back to client
                client_socket.send(json.dumps(response).encode('utf-8'))
        
        except Exception as e:
            self.logger.error(f"Error handling client {address}: {e}")
        
        finally:
            # Clean up
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            
            try:
                client_socket.close()
            except:
                pass
            
            self.logger.info(f"Connection closed: {address[0]}:{address[1]}")
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a client request.
        
        Args:
            request: Client request dictionary
            
        Returns:
            Response dictionary
        """
        if not isinstance(request, dict):
            return format_response(False, error="Invalid request format")
        
        if 'operation' not in request:
            return format_response(False, error="Missing operation field")
        
        operation = request['operation'].lower()
        
        # Database operations
        if operation == 'list_databases':
            return self._list_databases()
        
        elif operation == 'create_database':
            if 'database' not in request:
                return format_response(False, error="Missing database name")
            return self._create_database(request['database'])
        
        elif operation == 'drop_database':
            if 'database' not in request:
                return format_response(False, error="Missing database name")
            return self._drop_database(request['database'])
        
        # Collection operations
        elif operation == 'list_collections':
            if 'database' not in request:
                return format_response(False, error="Missing database name")
            return self._list_collections(request['database'])
        
        elif operation == 'create_collection':
            if 'database' not in request or 'collection' not in request:
                return format_response(False, error="Missing database or collection name")
            return self._create_collection(request['database'], request['collection'])
        
        # Document operations
        elif operation == 'insert':
            if not all(k in request for k in ['database', 'collection', 'document']):
                return format_response(False, error="Missing required fields")
            return self._insert_document(
                request['database'], 
                request['collection'], 
                request['document']
            )
        
        elif operation == 'find':
            if not all(k in request for k in ['database', 'collection']):
                return format_response(False, error="Missing required fields")
            query = request.get('query', {})
            return self._find_documents(request['database'], request['collection'], query)
        
        elif operation == 'update':
            if not all(k in request for k in ['database', 'collection', 'query', 'update']):
                return format_response(False, error="Missing required fields")
            return self._update_documents(
                request['database'], 
                request['collection'], 
                request['query'], 
                request['update']
            )
        
        elif operation == 'delete':
            if not all(k in request for k in ['database', 'collection', 'query']):
                return format_response(False, error="Missing required fields")
            return self._delete_documents(
                request['database'], 
                request['collection'], 
                request['query']
            )
        
        elif operation == 'create_index':
            return self._handle_create_index(request)
        
        elif operation == 'drop_index':
            return self._handle_drop_index(request)
        
        elif operation == 'list_indices':
            return self._handle_list_indices(request)
        
        else:
            return format_response(False, error=f"Unknown operation: {operation}")
    
    def _get_database(self, db_name: str) -> Database:
        """
        Get a database instance, using cache if possible.
        
        Args:
            db_name: Database name
            
        Returns:
            Database instance
        """
        if db_name not in self.db_cache:
            self.db_cache[db_name] = Database(db_name, self.config['data_dir'])
        
        return self.db_cache[db_name]
    
    def _list_databases(self) -> Dict[str, Any]:
        """
        List all databases.
        
        Returns:
            Response with database list
        """
        try:
            databases = list_databases(self.config['data_dir'])
            return format_response(True, data=databases)
        except Exception as e:
            self.logger.error(f"Error listing databases: {e}")
            return format_response(False, error=str(e))
    
    def _create_database(self, db_name: str) -> Dict[str, Any]:
        """
        Create a new database.
        
        Args:
            db_name: Database name
            
        Returns:
            Response indicating success or failure
        """
        try:
            database = self._get_database(db_name)
            return format_response(True)
        except Exception as e:
            self.logger.error(f"Error creating database: {e}")
            return format_response(False, error=str(e))
    
    def _drop_database(self, db_name: str) -> Dict[str, Any]:
        """
        Drop a database.
        
        Args:
            db_name: Database name
            
        Returns:
            Response indicating success or failure
        """
        try:
            db_path = os.path.join(self.config['data_dir'], db_name)
            
            if not os.path.exists(db_path):
                return format_response(False, error=f"Database '{db_name}' does not exist")
            
            # Remove from cache if present
            if db_name in self.db_cache:
                del self.db_cache[db_name]
            
            # Remove database directory recursively
            import shutil
            shutil.rmtree(db_path)
            
            return format_response(True)
        except Exception as e:
            self.logger.error(f"Error dropping database: {e}")
            return format_response(False, error=str(e))
    
    def _list_collections(self, db_name: str) -> Dict[str, Any]:
        """
        List collections in a database.
        
        Args:
            db_name: Database name
            
        Returns:
            Response with collection list
        """
        try:
            database = self._get_database(db_name)
            collections = database.list_collections()
            return format_response(True, data=collections)
        except Exception as e:
            self.logger.error(f"Error listing collections: {e}")
            return format_response(False, error=str(e))
    
    def _create_collection(self, db_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Create a new collection in a database.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            
        Returns:
            Response indicating success or failure
        """
        try:
            database = self._get_database(db_name)
            collection = database.collection(collection_name)
            return format_response(True)
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            return format_response(False, error=str(e))
    
    def _insert_document(self, db_name: str, collection_name: str, 
                         document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert a document into a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            document: Document to insert
            
        Returns:
            Response with document ID
        """
        try:
            database = self._get_database(db_name)
            collection = database.collection(collection_name)
            doc_id = collection.insert(document)
            return format_response(True, data={'_id': doc_id})
        except Exception as e:
            self.logger.error(f"Error inserting document: {e}")
            return format_response(False, error=str(e))
    
    def _find_documents(self, db_name: str, collection_name: str, 
                        query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find documents in a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            query: Query filter
            
        Returns:
            Response with matching documents
        """
        try:
            database = self._get_database(db_name)
            collection = database.collection(collection_name)
            documents = collection.find(query)
            return format_response(True, data=documents)
        except Exception as e:
            self.logger.error(f"Error finding documents: {e}")
            return format_response(False, error=str(e))
    
    def _update_documents(self, db_name: str, collection_name: str,
                          query: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update documents in a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            query: Query filter
            update: Update operations
            
        Returns:
            Response with count of updated documents
        """
        try:
            database = self._get_database(db_name)
            collection = database.collection(collection_name)
            updated_count = collection.update(query, update)
            return format_response(True, data={'updated_count': updated_count})
        except Exception as e:
            self.logger.error(f"Error updating documents: {e}")
            return format_response(False, error=str(e))
    
    def _delete_documents(self, db_name: str, collection_name: str,
                          query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete documents from a collection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            query: Query filter
            
        Returns:
            Response with count of deleted documents
        """
        try:
            database = self._get_database(db_name)
            collection = database.collection(collection_name)
            deleted_count = collection.delete(query)
            return format_response(True, data={'deleted_count': deleted_count})
        except Exception as e:
            self.logger.error(f"Error deleting documents: {e}")
            return format_response(False, error=str(e))
            
    def _handle_create_index(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle create index request.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        try:
            db_name = request.get('db_name')
            collection_name = request.get('collection_name')
            field = request.get('field')
            
            if not db_name:
                return {'success': False, 'error': 'Database name is required'}
            if not collection_name:
                return {'success': False, 'error': 'Collection name is required'}
            if not field:
                return {'success': False, 'error': 'Field name is required'}
            
            db = Database(db_name, self.config['data_dir'])
            if not db.exists():
                return {'success': False, 'error': f"Database '{db_name}' does not exist"}
            
            if not db.collection_exists(collection_name):
                return {'success': False, 'error': f"Collection '{collection_name}' does not exist"}
            
            collection = db.get_collection(collection_name)
            result = collection.create_index(field)
            
            return {'success': True, 'data': {'indexed': field}}
        except Exception as e:
            self.logger.error(f"Error creating index: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_drop_index(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle drop index request.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        try:
            db_name = request.get('db_name')
            collection_name = request.get('collection_name')
            field = request.get('field')
            
            if not db_name:
                return {'success': False, 'error': 'Database name is required'}
            if not collection_name:
                return {'success': False, 'error': 'Collection name is required'}
            if not field:
                return {'success': False, 'error': 'Field name is required'}
            
            db = Database(db_name, self.config['data_dir'])
            if not db.exists():
                return {'success': False, 'error': f"Database '{db_name}' does not exist"}
            
            if not db.collection_exists(collection_name):
                return {'success': False, 'error': f"Collection '{collection_name}' does not exist"}
            
            collection = db.get_collection(collection_name)
            result = collection.drop_index(field)
            
            if result:
                return {'success': True, 'data': {'dropped': field}}
            else:
                return {'success': False, 'error': f"Index on field '{field}' does not exist"}
        except Exception as e:
            self.logger.error(f"Error dropping index: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _handle_list_indices(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle list indices request.
        
        Args:
            request: Request dictionary
            
        Returns:
            Response dictionary
        """
        try:
            db_name = request.get('db_name')
            collection_name = request.get('collection_name')
            
            if not db_name:
                return {'success': False, 'error': 'Database name is required'}
            if not collection_name:
                return {'success': False, 'error': 'Collection name is required'}
            
            db = Database(db_name, self.config['data_dir'])
            if not db.exists():
                return {'success': False, 'error': f"Database '{db_name}' does not exist"}
            
            if not db.collection_exists(collection_name):
                return {'success': False, 'error': f"Collection '{collection_name}' does not exist"}
            
            collection = db.get_collection(collection_name)
            indices = collection.list_indices()
            
            return {'success': True, 'data': indices}
        except Exception as e:
            self.logger.error(f"Error listing indices: {str(e)}")
            return {'success': False, 'error': str(e)}
