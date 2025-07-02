#!/usr/bin/env python3
"""
DigitoolDB Web Dashboard Example

This example demonstrates how to create a simple web dashboard
for visualizing and interacting with DigitoolDB data.

Requirements:
- Flask (pip install flask)
- Bootstrap (included via CDN)
- Chart.js (included via CDN)
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import threading

# Add the parent directory to the Python path to import the DigitoolDB modules
sys.path.append(str(Path(__file__).parent.parent))

try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for
except ImportError:
    print("This example requires Flask. Install it with 'pip install flask'")
    sys.exit(1)

from src.client.simple_api import SimpleDB
from src.server.server import DigitoolDBServer

# Create Flask app
app = Flask(__name__)

# Initialize DigitoolDB server and client
db_server = None
db = None


# HTML template stored as a string (for simplicity in this example)
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DigitoolDB Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { padding-top: 20px; }
        .card { margin-bottom: 20px; }
        .stats-card { height: 140px; }
        .sidebar { background-color: #f8f9fa; padding: 20px; height: 100vh; }
        .main-content { padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <h4>DigitoolDB</h4>
                <hr>
                <div class="mb-3">
                    <label for="dbSelect" class="form-label">Databases</label>
                    <select id="dbSelect" class="form-select" onchange="changeDatabase()">
                        <option value="">Select Database</option>
                        {% for db_name in databases %}
                        <option value="{{ db_name }}" {% if current_db == db_name %}selected{% endif %}>{{ db_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                {% if current_db %}
                <div class="mb-3">
                    <label for="collectionSelect" class="form-label">Collections</label>
                    <select id="collectionSelect" class="form-select" onchange="changeCollection()">
                        <option value="">Select Collection</option>
                        {% for coll_name in collections %}
                        <option value="{{ coll_name }}" {% if current_collection == coll_name %}selected{% endif %}>{{ coll_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                {% endif %}
                <div class="d-grid gap-2 mt-4">
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createDbModal">Create Database</button>
                    {% if current_db %}
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createCollectionModal">Create Collection</button>
                    {% endif %}
                    {% if current_db and current_collection %}
                    <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#insertDocumentModal">Insert Document</button>
                    {% endif %}
                </div>
            </div>
            
            <!-- Main content -->
            <div class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {% if not current_db %}
                <div class="alert alert-info">
                    Select a database from the sidebar or create a new one to get started.
                </div>
                {% elif not current_collection %}
                <div class="alert alert-info">
                    Select a collection from the sidebar or create a new one to view documents.
                </div>
                {% else %}
                <!-- Stats cards -->
                <div class="row">
                    <div class="col-md-4">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h5 class="card-title">Total Documents</h5>
                                <h2 class="card-text">{{ document_count }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h5 class="card-title">Avg Document Size</h5>
                                <h2 class="card-text">{{ avg_size }} KB</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card stats-card">
                            <div class="card-body">
                                <h5 class="card-title">Indices</h5>
                                <h2 class="card-text">{{ index_count }}</h2>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Charts -->
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Field Distribution</h5>
                                <canvas id="fieldsChart"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Document Age</h5>
                                <canvas id="ageChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Documents table -->
                <div class="card mt-3">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5>Documents</h5>
                        <div class="input-group" style="width: 300px;">
                            <input type="text" id="searchInput" class="form-control" placeholder="Search...">
                            <button class="btn btn-outline-secondary" onclick="searchDocuments()">Search</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Preview</th>
                                        <th>Created</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for doc in documents %}
                                    <tr>
                                        <td>{{ doc._id }}</td>
                                        <td>{{ doc | preview }}</td>
                                        <td>{{ doc._created_at if doc._created_at else 'N/A' }}</td>
                                        <td>
                                            <button class="btn btn-sm btn-info" onclick="viewDocument('{{ doc._id }}')">View</button>
                                            <button class="btn btn-sm btn-danger" onclick="deleteDocument('{{ doc._id }}')">Delete</button>
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- Create Database Modal -->
    <div class="modal fade" id="createDbModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Database</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="createDbForm" action="/create_db" method="post">
                        <div class="mb-3">
                            <label for="dbName" class="form-label">Database Name</label>
                            <input type="text" class="form-control" id="dbName" name="dbName" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Create</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Create Collection Modal -->
    <div class="modal fade" id="createCollectionModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Collection</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="createCollectionForm" action="/create_collection" method="post">
                        <input type="hidden" name="dbName" value="{{ current_db }}">
                        <div class="mb-3">
                            <label for="collectionName" class="form-label">Collection Name</label>
                            <input type="text" class="form-control" id="collectionName" name="collectionName" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Create</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Insert Document Modal -->
    <div class="modal fade" id="insertDocumentModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Insert Document</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="insertDocumentForm" action="/insert_document" method="post">
                        <input type="hidden" name="dbName" value="{{ current_db }}">
                        <input type="hidden" name="collectionName" value="{{ current_collection }}">
                        <div class="mb-3">
                            <label for="documentJson" class="form-label">Document JSON</label>
                            <textarea class="form-control" id="documentJson" name="documentJson" rows="10" required>{ }</textarea>
                            <div class="form-text">Enter a valid JSON document</div>
                        </div>
                        <button type="submit" class="btn btn-primary">Insert</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    
    <!-- View Document Modal -->
    <div class="modal fade" id="viewDocumentModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Document Details</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <pre id="documentDetails" class="bg-light p-3 rounded"></pre>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Functions for navigation and CRUD operations
        function changeDatabase() {
            const dbName = document.getElementById('dbSelect').value;
            window.location.href = '/db/' + dbName;
        }
        
        function changeCollection() {
            const dbName = '{{ current_db }}';
            const collName = document.getElementById('collectionSelect').value;
            window.location.href = '/db/' + dbName + '/collection/' + collName;
        }
        
        function viewDocument(id) {
            fetch('/api/document/{{ current_db }}/{{ current_collection }}/' + id)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('documentDetails').textContent = JSON.stringify(data, null, 2);
                    new bootstrap.Modal(document.getElementById('viewDocumentModal')).show();
                });
        }
        
        function deleteDocument(id) {
            if (confirm('Are you sure you want to delete this document?')) {
                fetch('/api/document/{{ current_db }}/{{ current_collection }}/' + id, {
                    method: 'DELETE'
                }).then(() => window.location.reload());
            }
        }
        
        function searchDocuments() {
            const query = document.getElementById('searchInput').value;
            window.location.href = '/db/{{ current_db }}/collection/{{ current_collection }}?search=' + encodeURIComponent(query);
        }
        
        // Charts setup
        {% if current_db and current_collection %}
        document.addEventListener('DOMContentLoaded', function() {
            // Field distribution chart
            const fieldCtx = document.getElementById('fieldsChart').getContext('2d');
            new Chart(fieldCtx, {
                type: 'pie',
                data: {
                    labels: {{ field_labels | safe }},
                    datasets: [{
                        data: {{ field_counts | safe }},
                        backgroundColor: [
                            '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
                            '#5a5c69', '#858796', '#6f42c1', '#20c9a6', '#27a844'
                        ]
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    legend: {
                        position: 'right'
                    }
                }
            });
            
            // Document age chart
            const ageCtx = document.getElementById('ageChart').getContext('2d');
            new Chart(ageCtx, {
                type: 'bar',
                data: {
                    labels: {{ age_labels | safe }},
                    datasets: [{
                        label: 'Documents',
                        data: {{ age_counts | safe }},
                        backgroundColor: '#4e73df'
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
        {% endif %}
    </script>
</body>
</html>
"""


@app.template_filter('preview')
def preview_filter(doc):
    """Create a preview of the document"""
    # Remove _id and timestamps for preview
    preview_doc = {k: v for k, v in doc.items() if k not in ('_id', '_created_at', '_updated_at')}
    # Convert to string and truncate
    preview_str = str(preview_doc)
    if len(preview_str) > 70:
        preview_str = preview_str[:67] + "..."
    return preview_str


@app.route('/')
def index():
    """Home page route"""
    client = get_db_client()
    databases = client.list_dbs()
    
    return render_template_string(
        INDEX_TEMPLATE,
        databases=databases,
        current_db=None,
        current_collection=None,
        collections=[],
        documents=[],
        document_count=0,
        avg_size=0,
        index_count=0,
        field_labels=[],
        field_counts=[],
        age_labels=[],
        age_counts=[]
    )


@app.route('/db/<db_name>')
def view_database(db_name):
    """View database page"""
    client = get_db_client()
    databases = client.list_dbs()
    
    # Validate database exists
    if db_name not in databases:
        return redirect(url_for('index'))
    
    # Get collections
    db_obj = client.db(db_name)
    collections = db_obj.list_collections()
    
    return render_template_string(
        INDEX_TEMPLATE,
        databases=databases,
        current_db=db_name,
        current_collection=None,
        collections=collections,
        documents=[],
        document_count=0,
        avg_size=0,
        index_count=0,
        field_labels=[],
        field_counts=[],
        age_labels=[],
        age_counts=[]
    )


@app.route('/db/<db_name>/collection/<collection_name>')
def view_collection(db_name, collection_name):
    """View collection page"""
    client = get_db_client()
    databases = client.list_dbs()
    
    # Validate database exists
    if db_name not in databases:
        return redirect(url_for('index'))
    
    # Get collections
    db_obj = client.db(db_name)
    collections = db_obj.list_collections()
    
    # Validate collection exists
    if collection_name not in collections:
        return redirect(url_for('view_database', db_name=db_name))
    
    # Get documents
    collection = db_obj.collection(collection_name)
    search_query = request.args.get('search', '')
    
    if search_query:
        try:
            # Try to parse as JSON if it's a valid JSON string
            query = json.loads(search_query)
            documents = collection.find(query)
        except json.JSONDecodeError:
            # If not valid JSON, do a simple string search in all fields
            all_docs = collection.find()
            documents = []
            search_lower = search_query.lower()
            for doc in all_docs:
                doc_str = str(doc).lower()
                if search_lower in doc_str:
                    documents.append(doc)
    else:
        documents = collection.find()
    
    # Get statistics
    document_count = len(documents)
    
    # Calculate average document size
    avg_size = 0
    if document_count > 0:
        total_size = sum(len(json.dumps(doc)) for doc in documents)
        avg_size = round(total_size / document_count / 1024, 2)  # in KB
    
    # Get indices
    indices = collection.list_indices()
    index_count = len(indices)
    
    # Prepare chart data - field distribution
    field_counts = {}
    for doc in documents:
        for field in doc.keys():
            if field not in ('_id', '_created_at', '_updated_at'):
                field_counts[field] = field_counts.get(field, 0) + 1
    
    field_labels = list(field_counts.keys())
    field_values = list(field_counts.values())
    
    # Prepare chart data - document age
    age_groups = {
        'Today': 0,
        'This Week': 0,
        'This Month': 0,
        'Older': 0
    }
    
    today = datetime.now().date()
    for doc in documents:
        created_at = doc.get('_created_at')
        if not created_at:
            continue
        
        try:
            created_date = datetime.fromisoformat(created_at).date()
            days_old = (today - created_date).days
            
            if days_old == 0:
                age_groups['Today'] += 1
            elif days_old <= 7:
                age_groups['This Week'] += 1
            elif days_old <= 30:
                age_groups['This Month'] += 1
            else:
                age_groups['Older'] += 1
        except (ValueError, TypeError):
            continue
    
    age_labels = list(age_groups.keys())
    age_counts = list(age_groups.values())
    
    return render_template_string(
        INDEX_TEMPLATE,
        databases=databases,
        current_db=db_name,
        current_collection=collection_name,
        collections=collections,
        documents=documents,
        document_count=document_count,
        avg_size=avg_size,
        index_count=index_count,
        field_labels=json.dumps(field_labels),
        field_counts=json.dumps(field_values),
        age_labels=json.dumps(age_labels),
        age_counts=json.dumps(age_counts)
    )


@app.route('/create_db', methods=['POST'])
def create_database():
    """Create a new database"""
    db_name = request.form.get('dbName')
    if db_name:
        client = get_db_client()
        client.create_db(db_name)
    return redirect(url_for('view_database', db_name=db_name))


@app.route('/create_collection', methods=['POST'])
def create_collection():
    """Create a new collection"""
    db_name = request.form.get('dbName')
    collection_name = request.form.get('collectionName')
    if db_name and collection_name:
        client = get_db_client()
        db_obj = client.db(db_name)
        db_obj.create_collection(collection_name)
    return redirect(url_for('view_collection', db_name=db_name, collection_name=collection_name))


@app.route('/insert_document', methods=['POST'])
def insert_document():
    """Insert a document into a collection"""
    db_name = request.form.get('dbName')
    collection_name = request.form.get('collectionName')
    document_json = request.form.get('documentJson')
    
    if db_name and collection_name and document_json:
        try:
            document = json.loads(document_json)
            client = get_db_client()
            db_obj = client.db(db_name)
            collection = db_obj.collection(collection_name)
            collection.insert(document)
        except json.JSONDecodeError:
            # Handle invalid JSON
            pass
    
    return redirect(url_for('view_collection', db_name=db_name, collection_name=collection_name))


@app.route('/api/document/<db_name>/<collection_name>/<doc_id>', methods=['GET'])
def get_document(db_name, collection_name, doc_id):
    """API to get a single document"""
    client = get_db_client()
    db_obj = client.db(db_name)
    collection = db_obj.collection(collection_name)
    document = collection.find_one({'_id': doc_id})
    
    if document:
        return jsonify(document)
    else:
        return jsonify({'error': 'Document not found'}), 404


@app.route('/api/document/<db_name>/<collection_name>/<doc_id>', methods=['DELETE'])
def delete_document(db_name, collection_name, doc_id):
    """API to delete a document"""
    client = get_db_client()
    db_obj = client.db(db_name)
    collection = db_obj.collection(collection_name)
    result = collection.delete({'_id': doc_id})
    
    if result > 0:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Document not found'}), 404


def get_db_client():
    """Get or create a database client"""
    global db
    if db is None or not db.connected:
        db = SimpleDB()
        db.connect()
    return db


def start_db_server():
    """Start the DigitoolDB server"""
    global db_server
    if db_server is None:
        db_server = DigitoolDBServer()
        server_thread = threading.Thread(target=db_server.start)
        server_thread.daemon = True
        server_thread.start()
        print("DigitoolDB server started")
        # Wait for server to start
        time.sleep(1)


def setup_sample_data():
    """Set up some sample data for demonstration"""
    client = get_db_client()
    
    # Create sample database if it doesn't exist
    if "dashboard_demo" not in client.list_dbs():
        print("Creating sample data...")
        client.create_db("dashboard_demo")
        db_obj = client.db("dashboard_demo")
        
        # Create products collection
        db_obj.create_collection("products")
        products = db_obj.collection("products")
        
        # Create indices
        products.create_index("category")
        products.create_index("price")
        
        # Insert sample products
        sample_products = [
            {
                "name": "Laptop",
                "category": "Electronics",
                "price": 999.99,
                "stock": 45,
                "features": ["8GB RAM", "256GB SSD", "15.6 inch display"]
            },
            {
                "name": "Smartphone",
                "category": "Electronics",
                "price": 699.99,
                "stock": 120,
                "features": ["6.5 inch display", "128GB storage", "Dual camera"]
            },
            {
                "name": "Coffee Maker",
                "category": "Kitchen",
                "price": 89.99,
                "stock": 30,
                "features": ["Programmable", "12-cup carafe", "Auto shut-off"]
            },
            {
                "name": "Running Shoes",
                "category": "Sports",
                "price": 129.99,
                "stock": 75,
                "features": ["Lightweight", "Breathable", "Cushioned sole"]
            },
            {
                "name": "Desk Lamp",
                "category": "Home",
                "price": 34.99,
                "stock": 50,
                "features": ["Adjustable", "LED bulb", "USB charging port"]
            }
        ]
        
        for product in sample_products:
            products.insert(product)
        
        # Create customers collection
        db_obj.create_collection("customers")
        customers = db_obj.collection("customers")
        
        # Create indices
        customers.create_index("email")
        
        # Insert sample customers
        sample_customers = [
            {
                "name": "John Smith",
                "email": "john@example.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "zip": "12345"
                },
                "membership": "gold"
            },
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "address": {
                    "street": "456 Oak Ave",
                    "city": "Somewhere",
                    "zip": "67890"
                },
                "membership": "silver"
            },
            {
                "name": "Bob Johnson",
                "email": "bob@example.com",
                "address": {
                    "street": "789 Pine Rd",
                    "city": "Nowhere",
                    "zip": "54321"
                },
                "membership": "bronze"
            }
        ]
        
        for customer in sample_customers:
            customers.insert(customer)
        
        print("Sample data created")


def main():
    """Main function to start the web dashboard"""
    print("DigitoolDB Web Dashboard Example")
    print("===============================")
    print("\nStarting DigitoolDB server...")
    
    # Start database server
    start_db_server()
    
    # Set up sample data
    setup_sample_data()
    
    # Start Flask app
    print("\nStarting web dashboard...")
    print("Open your browser and navigate to http://localhost:5000")
    app.run(debug=True)


if __name__ == '__main__':
    main()
