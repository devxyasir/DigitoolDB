"""
Unit tests for DigitoolDB models
"""
import json
import os
import shutil
import tempfile
import unittest

from src.common.models import Document, Collection, Database


class TestDocument(unittest.TestCase):
    """Tests for the Document class"""
    
    def test_create_document(self):
        """Test creating a document"""
        data = {'name': 'Test', 'value': 123}
        doc = Document(data)
        
        # Check ID generation
        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.data['_id'], doc.id)
        
        # Check metadata fields
        self.assertIn('_created_at', doc.data)
        self.assertIn('_updated_at', doc.data)
        
        # Check data integrity
        self.assertEqual(doc.data['name'], 'Test')
        self.assertEqual(doc.data['value'], 123)
    
    def test_create_document_with_id(self):
        """Test creating a document with a predefined ID"""
        data = {'name': 'Test', '_id': 'custom-id'}
        doc = Document(data, 'custom-id')
        
        # Check ID usage
        self.assertEqual(doc.id, 'custom-id')
        self.assertEqual(doc.data['_id'], 'custom-id')
    
    def test_document_to_json(self):
        """Test converting document to JSON"""
        data = {'name': 'Test', 'value': 123}
        doc = Document(data)
        
        json_str = doc.to_json()
        parsed = json.loads(json_str)
        
        # Check serialization
        self.assertEqual(parsed['name'], 'Test')
        self.assertEqual(parsed['value'], 123)
        self.assertEqual(parsed['_id'], doc.id)
    
    def test_document_from_json(self):
        """Test creating document from JSON"""
        data = {'name': 'Test', 'value': 123, '_id': 'test-id'}
        json_str = json.dumps(data)
        
        doc = Document.from_json(json_str)
        
        # Check deserialization
        self.assertEqual(doc.id, 'test-id')
        self.assertEqual(doc.data['name'], 'Test')
        self.assertEqual(doc.data['value'], 123)


class TestCollection(unittest.TestCase):
    """Tests for the Collection class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.collection = Collection('test_collection', self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_collection_creation(self):
        """Test collection creation"""
        # Check file creation
        collection_path = os.path.join(self.temp_dir, 'test_collection.digitool')
        self.assertTrue(os.path.exists(collection_path))
        
        # Check initial content
        with open(collection_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, '[]')
    
    def test_insert_document(self):
        """Test inserting a document"""
        doc_data = {'name': 'Test', 'value': 123}
        doc_id = self.collection.insert(doc_data)
        
        # Check returned ID
        self.assertIsNotNone(doc_id)
        
        # Check document was saved
        documents = self.collection._read_collection()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]['name'], 'Test')
        self.assertEqual(documents[0]['value'], 123)
        self.assertEqual(documents[0]['_id'], doc_id)
    
    def test_find_documents(self):
        """Test finding documents"""
        # Insert test documents
        self.collection.insert({'name': 'Alice', 'age': 30})
        self.collection.insert({'name': 'Bob', 'age': 25})
        self.collection.insert({'name': 'Charlie', 'age': 35})
        
        # Find all documents
        all_docs = self.collection.find()
        self.assertEqual(len(all_docs), 3)
        
        # Find with query
        alice_docs = self.collection.find({'name': 'Alice'})
        self.assertEqual(len(alice_docs), 1)
        self.assertEqual(alice_docs[0]['age'], 30)
        
        # Find with age query
        young_docs = self.collection.find({'age': 25})
        self.assertEqual(len(young_docs), 1)
        self.assertEqual(young_docs[0]['name'], 'Bob')
        
        # Find with non-matching query
        no_docs = self.collection.find({'name': 'David'})
        self.assertEqual(len(no_docs), 0)
    
    def test_update_documents(self):
        """Test updating documents"""
        # Insert test documents
        self.collection.insert({'name': 'Alice', 'age': 30})
        self.collection.insert({'name': 'Bob', 'age': 25})
        
        # Update with $set
        updated = self.collection.update(
            {'name': 'Alice'}, 
            {'$set': {'age': 31}}
        )
        self.assertEqual(updated, 1)
        
        # Check document was updated
        alice = self.collection.find({'name': 'Alice'})[0]
        self.assertEqual(alice['age'], 31)
        
        # Update multiple documents
        self.collection.insert({'name': 'Charlie', 'age': 25})
        updated = self.collection.update(
            {'age': 25}, 
            {'$set': {'status': 'active'}}
        )
        self.assertEqual(updated, 2)
        
        # Check documents were updated
        active_docs = self.collection.find({'status': 'active'})
        self.assertEqual(len(active_docs), 2)
    
    def test_delete_documents(self):
        """Test deleting documents"""
        # Insert test documents
        self.collection.insert({'name': 'Alice', 'age': 30})
        self.collection.insert({'name': 'Bob', 'age': 25})
        self.collection.insert({'name': 'Charlie', 'age': 25})
        
        # Delete one document
        deleted = self.collection.delete({'name': 'Alice'})
        self.assertEqual(deleted, 1)
        
        # Check document was deleted
        all_docs = self.collection.find()
        self.assertEqual(len(all_docs), 2)
        self.assertNotIn('Alice', [doc['name'] for doc in all_docs])
        
        # Delete multiple documents
        deleted = self.collection.delete({'age': 25})
        self.assertEqual(deleted, 2)
        
        # Check documents were deleted
        all_docs = self.collection.find()
        self.assertEqual(len(all_docs), 0)


class TestDatabase(unittest.TestCase):
    """Tests for the Database class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db = Database('test_db', self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_database_creation(self):
        """Test database creation"""
        # Check directory creation
        db_path = os.path.join(self.temp_dir, 'test_db')
        self.assertTrue(os.path.exists(db_path))
        self.assertTrue(os.path.isdir(db_path))
    
    def test_get_collection(self):
        """Test getting a collection"""
        collection = self.db.collection('test_collection')
        
        # Check collection creation
        self.assertEqual(collection.name, 'test_collection')
        
        # Check file creation
        collection_path = os.path.join(self.temp_dir, 'test_db', 'test_collection.digitool')
        self.assertTrue(os.path.exists(collection_path))
    
    def test_list_collections(self):
        """Test listing collections"""
        # Initially no collections
        collections = self.db.list_collections()
        self.assertEqual(len(collections), 0)
        
        # Create some collections
        self.db.collection('collection1')
        self.db.collection('collection2')
        
        # Check list
        collections = self.db.list_collections()
        self.assertEqual(len(collections), 2)
        self.assertIn('collection1', collections)
        self.assertIn('collection2', collections)


if __name__ == '__main__':
    unittest.main()
