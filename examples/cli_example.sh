#!/bin/bash
# DigitoolDB CLI Example
# This script demonstrates the usage of the digi CLI tool

# Start the server in the background (for demo purposes)
echo "Starting DigitoolDB server..."
digid &
SERVER_PID=$!

# Wait for server to start
sleep 2
echo "Server started with PID: $SERVER_PID"

echo -e "\n--- Creating a database ---"
digi create-db test_db

echo -e "\n--- Creating a collection ---"
digi create-collection test_db users

echo -e "\n--- Inserting documents ---"
digi insert test_db users '{"name": "Yasir", "age": 30, "email": "yasir@example.com"}'
digi insert test_db users '{"name": "Ahmed", "age": 28, "email": "ahmed@example.com"}'
digi insert test_db users '{"name": "Sara", "age": 32, "email": "sara@example.com"}'

echo -e "\n--- Listing all users ---"
digi find test_db users --pretty

echo -e "\n--- Finding users with specific criteria ---"
digi find test_db users '{"age": 30}' --pretty

echo -e "\n--- Updating a document ---"
digi update test_db users '{"name": "Yasir"}' '{"$set": {"age": 31}}' --pretty

echo -e "\n--- Verify update ---"
digi find test_db users '{"name": "Yasir"}' --pretty

echo -e "\n--- Deleting a document ---"
digi delete test_db users '{"name": "Ahmed"}'

echo -e "\n--- Verify deletion ---"
digi find test_db users --pretty

echo -e "\n--- Listing all databases ---"
digi databases --pretty

echo -e "\n--- Listing all collections in test_db ---"
digi collections test_db --pretty

echo -e "\n--- Cleanup: Drop database ---"
digi drop-db test_db

echo -e "\n--- Stopping the server ---"
kill $SERVER_PID
echo "Server stopped"
