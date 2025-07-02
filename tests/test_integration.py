"""
Integration tests for DigitoolDB
These tests require a running server instance.
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from src.client.client import DigitoolDBClient
from src.server.server import DigitoolDBServer


class IntegrationTests(unittest.TestCase):
    """Integration tests for DigitoolDB server and client"""
    
    @classmethod
    def setUpClass(cls):
        """Start a test server"""
        # Create temporary data directory
        cls.temp_dir = tempfile.mkdtemp()
        
        # Create config file
        cls.config_file = os.path.join(cls.temp_dir, 'test_config.json')
        with open(cls.config_file, 'w') as f:
            json.dump({
                'host': '127.0.0.1',
                'port': 27018,  # Use different port from default
                'data_dir': os.path.join(cls.temp_dir, 'data'),
                'log_level': 'info',
                'log_file': os.path.join(cls.temp_dir, 'digitooldb.log'),
                'max_connections': 5,
                'timeout': 5
            }, f)
        
        # Start server in a separate thread
        cls.server = DigitoolDBServer(cls.config_file)
        cls.server_thread = threading.Thread(target=cls.server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Give server time to start
        time.sleep(1)
        
        # Create client
        cls.client = DigitoolDBClient(cls.config_file)
        
        # Connect to server
        connected = cls.client.connect()
        if not connected:
            raise Exception("Failed to connect to test server")
    
    @classmethod
    def tearDownClass(cls):
        """Stop the test server"""
        cls.client.disconnect()
        cls.server.stop()
        
        # Remove temporary directory
        import shutil
        shutil.rmtree(cls.temp_dir)
    
    def test_database_operations(self):
        """Test database operations"""
        # List databases (should be empty initially)
        response = self.client.list_databases()
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 0)
        
        # Create database
        response = self.client.create_database('test_db')
        self.assertTrue(response['success'])
        
        # List databases again
        response = self.client.list_databases()
        self.assertTrue(response['success'])
        self.assertIn('test_db', response['data'])
        
        # Try creating the same database again (should still succeed)
        response = self.client.create_database('test_db')
        self.assertTrue(response['success'])
        
        # Drop database
        response = self.client.drop_database('test_db')
        self.assertTrue(response['success'])
        
        # List databases again (should be empty)
        response = self.client.list_databases()
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 0)
    
    def test_collection_operations(self):
        """Test collection operations"""
        # Create database
        response = self.client.create_database('test_db')
        self.assertTrue(response['success'])
        
        # List collections (should be empty initially)
        response = self.client.list_collections('test_db')
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 0)
        
        # Create collection
        response = self.client.create_collection('test_db', 'test_collection')
        self.assertTrue(response['success'])
        
        # List collections again
        response = self.client.list_collections('test_db')
        self.assertTrue(response['success'])
        self.assertIn('test_collection', response['data'])
        
        # Clean up
        self.client.drop_database('test_db')
    
    def test_document_operations(self):
        """Test document operations"""
        # Create database and collection
        self.client.create_database('test_db')
        self.client.create_collection('test_db', 'users')
        
        # Insert document
        doc = {'name': 'Yasir', 'age': 30, 'email': 'yasir@example.com'}
        response = self.client.insert('test_db', 'users', doc)
        self.assertTrue(response['success'])
        self.assertIn('_id', response['data'])
        doc_id = response['data']['_id']
        
        # Find all documents
        response = self.client.find('test_db', 'users')
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['name'], 'Yasir')
        
        # Find with query
        response = self.client.find('test_db', 'users', {'name': 'Yasir'})
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 1)
        
        # Update document
        response = self.client.update(
            'test_db', 'users', 
            {'name': 'Yasir'}, 
            {'$set': {'age': 31}}
        )
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['updated_count'], 1)
        
        # Find to verify update
        response = self.client.find('test_db', 'users', {'name': 'Yasir'})
        self.assertTrue(response['success'])
        self.assertEqual(response['data'][0]['age'], 31)
        
        # Delete document
        response = self.client.delete('test_db', 'users', {'name': 'Yasir'})
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['deleted_count'], 1)
        
        # Find to verify deletion
        response = self.client.find('test_db', 'users')
        self.assertTrue(response['success'])
        self.assertEqual(len(response['data']), 0)
        
        # Clean up
        self.client.drop_database('test_db')


if __name__ == '__main__':
    unittest.main()
