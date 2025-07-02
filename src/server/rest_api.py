"""
REST API server for DigitoolDB
"""
import argparse
import json
import logging
import os
import sys
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from ..common.utils import (
    parse_json_input, 
    format_response, 
    get_default_config, 
    load_config
)
from .server import DigitoolDBServer


class DigitoolDBRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for DigitoolDB REST API"""
    
    server_version = "DigitoolDB/0.1"
    
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('digitooldb.rest')
        super().__init__(*args, **kwargs)
    
    def _set_headers(self, status_code=HTTPStatus.OK, content_type='application/json'):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json_response(self, data, status_code=HTTPStatus.OK):
        """Send JSON response"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _read_request_body(self):
        """Read and parse request body as JSON"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        
        request_body = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(request_body)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in request body: {e}")
            return None
    
    def _parse_path(self):
        """Parse request path and query parameters"""
        url_parts = urlparse(self.path)
        path = url_parts.path.strip('/')
        query = parse_qs(url_parts.query)
        
        # Convert query parameters from lists to single values
        query_params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}
        
        # Split path into parts
        path_parts = path.split('/')
        
        return path_parts, query_params
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self._set_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path_parts, query_params = self._parse_path()
        server = self.server.db_server
        
        try:
            # Handle database and collection listing
            if not path_parts or path_parts[0] == '':
                # GET / - List databases
                response = server._list_databases()
                self._send_json_response(response)
            
            elif len(path_parts) == 1:
                # GET /database - List collections
                db_name = path_parts[0]
                response = server._list_collections(db_name)
                self._send_json_response(response)
            
            elif len(path_parts) == 2:
                # GET /database/collection - Find documents
                db_name = path_parts[0]
                collection_name = path_parts[1]
                
                # Parse query filter if present
                query = {}
                if 'filter' in query_params:
                    try:
                        query = json.loads(query_params['filter'])
                    except json.JSONDecodeError:
                        self._send_json_response(
                            format_response(False, error="Invalid filter JSON"),
                            HTTPStatus.BAD_REQUEST
                        )
                        return
                
                response = server._find_documents(db_name, collection_name, query)
                self._send_json_response(response)
            
            else:
                # Invalid path
                self._send_json_response(
                    format_response(False, error="Invalid path"),
                    HTTPStatus.NOT_FOUND
                )
        
        except Exception as e:
            self.logger.error(f"Error handling GET request: {e}")
            self._send_json_response(
                format_response(False, error=str(e)),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def do_POST(self):
        """Handle POST requests"""
        path_parts, _ = self._parse_path()
        request_body = self._read_request_body()
        server = self.server.db_server
        
        try:
            if request_body is None:
                self._send_json_response(
                    format_response(False, error="Invalid JSON in request body"),
                    HTTPStatus.BAD_REQUEST
                )
                return
            
            if len(path_parts) == 1:
                # POST /database - Create database
                db_name = path_parts[0]
                response = server._create_database(db_name)
                self._send_json_response(response)
            
            elif len(path_parts) == 2:
                # POST /database/collection - Create collection or insert document
                db_name = path_parts[0]
                collection_name = path_parts[1]
                
                if not request_body:
                    # Create collection if no document provided
                    response = server._create_collection(db_name, collection_name)
                else:
                    # Insert document
                    response = server._insert_document(db_name, collection_name, request_body)
                
                self._send_json_response(response)
            
            else:
                # Invalid path
                self._send_json_response(
                    format_response(False, error="Invalid path"),
                    HTTPStatus.NOT_FOUND
                )
        
        except Exception as e:
            self.logger.error(f"Error handling POST request: {e}")
            self._send_json_response(
                format_response(False, error=str(e)),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def do_PUT(self):
        """Handle PUT requests"""
        path_parts, _ = self._parse_path()
        request_body = self._read_request_body()
        server = self.server.db_server
        
        try:
            if request_body is None:
                self._send_json_response(
                    format_response(False, error="Invalid JSON in request body"),
                    HTTPStatus.BAD_REQUEST
                )
                return
            
            if len(path_parts) == 2:
                # PUT /database/collection - Update documents
                db_name = path_parts[0]
                collection_name = path_parts[1]
                
                if 'query' not in request_body or 'update' not in request_body:
                    self._send_json_response(
                        format_response(False, error="Missing query or update in request body"),
                        HTTPStatus.BAD_REQUEST
                    )
                    return
                
                response = server._update_documents(
                    db_name, 
                    collection_name, 
                    request_body['query'], 
                    request_body['update']
                )
                self._send_json_response(response)
            
            else:
                # Invalid path
                self._send_json_response(
                    format_response(False, error="Invalid path"),
                    HTTPStatus.NOT_FOUND
                )
        
        except Exception as e:
            self.logger.error(f"Error handling PUT request: {e}")
            self._send_json_response(
                format_response(False, error=str(e)),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        path_parts, query_params = self._parse_path()
        server = self.server.db_server
        
        try:
            if len(path_parts) == 1:
                # DELETE /database - Drop database
                db_name = path_parts[0]
                response = server._drop_database(db_name)
                self._send_json_response(response)
            
            elif len(path_parts) == 2:
                # DELETE /database/collection - Delete documents
                db_name = path_parts[0]
                collection_name = path_parts[1]
                
                # Get query from request body or query parameter
                query = {}
                request_body = self._read_request_body()
                
                if request_body and 'query' in request_body:
                    query = request_body['query']
                elif 'filter' in query_params:
                    try:
                        query = json.loads(query_params['filter'])
                    except json.JSONDecodeError:
                        self._send_json_response(
                            format_response(False, error="Invalid filter JSON"),
                            HTTPStatus.BAD_REQUEST
                        )
                        return
                
                response = server._delete_documents(db_name, collection_name, query)
                self._send_json_response(response)
            
            else:
                # Invalid path
                self._send_json_response(
                    format_response(False, error="Invalid path"),
                    HTTPStatus.NOT_FOUND
                )
        
        except Exception as e:
            self.logger.error(f"Error handling DELETE request: {e}")
            self._send_json_response(
                format_response(False, error=str(e)),
                HTTPStatus.INTERNAL_SERVER_ERROR
            )


class DigitoolDBRestServer:
    """REST API server for DigitoolDB"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the REST API server.
        
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
        
        # Add REST API specific config
        if 'rest_host' not in self.config:
            self.config['rest_host'] = '0.0.0.0'
        if 'rest_port' not in self.config:
            self.config['rest_port'] = 8000
        
        # Setup logging
        self._setup_logging()
        
        # Create DB server
        self.db_server = DigitoolDBServer(config_path)
        
        # Start DB server thread
        import threading
        self.db_thread = threading.Thread(target=self.db_server.start)
        self.db_thread.daemon = True
        
        # HTTP server
        self.http_server = None
    
    def _setup_logging(self):
        """
        Set up logging for the server.
        """
        log_dir = os.path.dirname(self.config['log_file'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logging.basicConfig(
            level=getattr(logging, self.config['log_level'].upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['log_file']),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('digitooldb.rest')
    
    def start(self):
        """Start the REST API server"""
        # Start DB server thread
        self.db_thread.start()
        
        # Wait for DB server to initialize
        import time
        time.sleep(1)
        
        # Create HTTP server
        server_address = (self.config['rest_host'], self.config['rest_port'])
        self.http_server = HTTPServer(server_address, DigitoolDBRequestHandler)
        self.http_server.db_server = self.db_server
        
        self.logger.info(f"REST API server started on {self.config['rest_host']}:{self.config['rest_port']}")
        print(f"REST API server started on {self.config['rest_host']}:{self.config['rest_port']}")
        
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the REST API server"""
        self.logger.info("Stopping REST API server...")
        
        if self.http_server:
            self.http_server.shutdown()
        
        self.db_server.stop()
        self.logger.info("REST API server stopped")


def main():
    """Main entry point for the REST API server"""
    parser = argparse.ArgumentParser(description='DigitoolDB REST API Server')
    parser.add_argument('--config', help='Path to config file')
    parser.add_argument('--host', help='REST API host')
    parser.add_argument('--port', type=int, help='REST API port')
    args = parser.parse_args()
    
    # Create server with config
    server = DigitoolDBRestServer(args.config)
    
    # Override config with command line arguments
    if args.host:
        server.config['rest_host'] = args.host
    if args.port:
        server.config['rest_port'] = args.port
    
    # Start server
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
