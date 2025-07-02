#!/usr/bin/env python3
"""
Todo List Application Example

This example shows how to build a simple todo list application
using DigitoolDB with the SimpleDB API. It demonstrates:

1. Basic CRUD operations
2. Using indices for performance
3. More complex queries
4. Data modeling best practices
"""
import sys
import time
from datetime import datetime
from pathlib import Path
import uuid

# Add the parent directory to the Python path to import the DigitoolDB modules
sys.path.append(str(Path(__file__).parent.parent))

from src.client.simple_api import SimpleDB
from src.server.server import DigitoolDBServer


class TodoApp:
    """Simple Todo List Application using DigitoolDB"""
    
    def __init__(self):
        """Initialize the Todo App"""
        self.db = SimpleDB()
        self.db.connect()
        
        # Set up database and collections
        if "todo_app" not in self.db.list_dbs():
            self.db.create_db("todo_app")
        
        self.todo_db = self.db.db("todo_app")
        
        # Create collections if they don't exist
        if "tasks" not in self.todo_db.list_collections():
            self.todo_db.create_collection("tasks")
            # Create indices for better performance
            tasks = self.todo_db.collection("tasks")
            tasks.create_index("completed")
            tasks.create_index("due_date")
            tasks.create_index("priority")
            tasks.create_index("category")
            print("Created tasks collection with indices")
        
        if "categories" not in self.todo_db.list_collections():
            self.todo_db.create_collection("categories")
            # Create a unique index on category name
            categories = self.todo_db.collection("categories")
            categories.create_index("name")
            print("Created categories collection with indices")
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'db') and self.db.connected:
            self.db.disconnect()
    
    def add_task(self, title, description=None, due_date=None, 
                priority="medium", category=None):
        """
        Add a new task to the todo list
        
        Args:
            title (str): Task title
            description (str, optional): Task description
            due_date (str, optional): Due date in YYYY-MM-DD format
            priority (str, optional): Priority (low, medium, high)
            category (str, optional): Task category
            
        Returns:
            str: ID of the created task
        """
        tasks = self.todo_db.collection("tasks")
        
        # Validate category exists if provided
        if category:
            self._ensure_category_exists(category)
        
        # Create task document
        task = {
            "title": title,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed": False,
            "priority": priority,
            "category": category
        }
        
        # Add due date if provided
        if due_date:
            task["due_date"] = due_date
        
        # Insert task and return ID
        task_id = tasks.insert(task)
        print(f"Added task: {title} (ID: {task_id})")
        return task_id
    
    def complete_task(self, task_id):
        """
        Mark a task as completed
        
        Args:
            task_id (str): ID of the task to complete
            
        Returns:
            bool: True if task was updated, False otherwise
        """
        tasks = self.todo_db.collection("tasks")
        
        # Update the task
        updated = tasks.update(
            {"_id": task_id},
            {"$set": {
                "completed": True,
                "updated_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }}
        )
        
        if updated > 0:
            print(f"Marked task {task_id} as completed")
            return True
        else:
            print(f"Task {task_id} not found")
            return False
    
    def delete_task(self, task_id):
        """
        Delete a task
        
        Args:
            task_id (str): ID of the task to delete
            
        Returns:
            bool: True if task was deleted, False otherwise
        """
        tasks = self.todo_db.collection("tasks")
        
        # Delete the task
        deleted = tasks.delete({"_id": task_id})
        
        if deleted > 0:
            print(f"Deleted task {task_id}")
            return True
        else:
            print(f"Task {task_id} not found")
            return False
    
    def update_task(self, task_id, **updates):
        """
        Update a task's properties
        
        Args:
            task_id (str): ID of the task to update
            **updates: Keyword arguments of properties to update
            
        Returns:
            bool: True if task was updated, False otherwise
        """
        tasks = self.todo_db.collection("tasks")
        
        # Validate category exists if provided
        if "category" in updates:
            self._ensure_category_exists(updates["category"])
        
        # Add updated_at timestamp
        updates["updated_at"] = datetime.now().isoformat()
        
        # Update the task
        updated = tasks.update(
            {"_id": task_id},
            {"$set": updates}
        )
        
        if updated > 0:
            print(f"Updated task {task_id}")
            return True
        else:
            print(f"Task {task_id} not found")
            return False
    
    def list_tasks(self, completed=None, category=None, priority=None, 
                  due_before=None, due_after=None):
        """
        List tasks with optional filtering
        
        Args:
            completed (bool, optional): Filter by completion status
            category (str, optional): Filter by category
            priority (str, optional): Filter by priority
            due_before (str, optional): Show tasks due before this date
            due_after (str, optional): Show tasks due after this date
            
        Returns:
            list: Matching tasks
        """
        tasks = self.todo_db.collection("tasks")
        
        # Build query
        query = {}
        
        if completed is not None:
            query["completed"] = completed
        
        if category:
            query["category"] = category
        
        if priority:
            query["priority"] = priority
        
        # Date range query
        if due_before or due_after:
            query["due_date"] = {}
            
            if due_before:
                query["due_date"]["$lte"] = due_before
                
            if due_after:
                query["due_date"]["$gte"] = due_after
        
        # Execute query
        results = tasks.find(query)
        
        # Display results
        if results:
            print(f"Found {len(results)} tasks:")
            for task in results:
                status = "✓" if task.get("completed") else "☐"
                print(f"{status} [{task.get('priority', 'medium')}] {task['title']}")
                if task.get("due_date"):
                    print(f"   Due: {task['due_date']}")
                if task.get("category"):
                    print(f"   Category: {task['category']}")
        else:
            print("No tasks found matching criteria.")
        
        return results
    
    def add_category(self, name, color=None):
        """
        Add a new category
        
        Args:
            name (str): Category name
            color (str, optional): Color code for the category
            
        Returns:
            str: ID of the created category or None if it already exists
        """
        categories = self.todo_db.collection("categories")
        
        # Check if category already exists
        existing = categories.find_one({"name": name})
        if existing:
            print(f"Category '{name}' already exists")
            return existing["_id"]
        
        # Create category
        category = {
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        if color:
            category["color"] = color
        
        # Insert category
        category_id = categories.insert(category)
        print(f"Added category: {name} (ID: {category_id})")
        return category_id
    
    def list_categories(self):
        """
        List all categories
        
        Returns:
            list: All categories
        """
        categories = self.todo_db.collection("categories")
        results = categories.find()
        
        if results:
            print(f"Found {len(results)} categories:")
            for category in results:
                print(f"- {category['name']}")
                if category.get("color"):
                    print(f"  Color: {category['color']}")
        else:
            print("No categories found.")
        
        return results
    
    def get_stats(self):
        """
        Get statistics about tasks
        
        Returns:
            dict: Task statistics
        """
        tasks = self.todo_db.collection("tasks")
        
        # Get all tasks
        all_tasks = tasks.find()
        total = len(all_tasks)
        
        # Count completed tasks
        completed = len([t for t in all_tasks if t.get("completed")])
        
        # Count tasks by priority
        priorities = {"high": 0, "medium": 0, "low": 0}
        for task in all_tasks:
            priority = task.get("priority", "medium")
            if priority in priorities:
                priorities[priority] += 1
        
        # Get tasks due today
        today = datetime.now().strftime("%Y-%m-%d")
        due_today = len(tasks.find({"due_date": today, "completed": False}))
        
        # Get overdue tasks
        overdue = len(tasks.find({
            "due_date": {"$lt": today},
            "completed": False
        }))
        
        # Build stats
        stats = {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "completion_rate": round(completed / total * 100, 1) if total > 0 else 0,
            "by_priority": priorities,
            "due_today": due_today,
            "overdue": overdue
        }
        
        # Display stats
        print("\n===== Task Statistics =====")
        print(f"Total Tasks: {stats['total']}")
        print(f"Completed: {stats['completed']} ({stats['completion_rate']}%)")
        print(f"Pending: {stats['pending']}")
        print(f"High Priority: {stats['by_priority']['high']}")
        print(f"Medium Priority: {stats['by_priority']['medium']}")
        print(f"Low Priority: {stats['by_priority']['low']}")
        print(f"Due Today: {stats['due_today']}")
        print(f"Overdue: {stats['overdue']}")
        print("==========================\n")
        
        return stats
    
    def _ensure_category_exists(self, category_name):
        """Helper method to ensure a category exists"""
        categories = self.todo_db.collection("categories")
        existing = categories.find_one({"name": category_name})
        
        if not existing:
            # Auto-create the category
            self.add_category(category_name)


def main():
    """Main example function"""
    print("DigitoolDB Todo List Example")
    print("===========================")
    
    # Start server in background
    print("\nStarting DigitoolDB server...")
    server = DigitoolDBServer()
    
    import threading
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(1)
    
    # Create and run the Todo App
    try:
        app = TodoApp()
        
        # Add some categories
        app.add_category("Work", "blue")
        app.add_category("Personal", "green")
        app.add_category("Health", "red")
        
        print("\nAdded categories:")
        app.list_categories()
        
        # Add some tasks
        print("\nAdding tasks:")
        app.add_task(
            title="Complete project proposal",
            description="Draft the project proposal for the client meeting",
            due_date="2025-06-10",
            priority="high",
            category="Work"
        )
        
        app.add_task(
            title="Go grocery shopping",
            description="Buy fruits, vegetables, and milk",
            due_date="2025-06-04",
            priority="medium",
            category="Personal"
        )
        
        app.add_task(
            title="Morning jog",
            description="30-minute jog in the park",
            due_date="2025-06-03",  # Today
            priority="low",
            category="Health"
        )
        
        app.add_task(
            title="Team meeting",
            description="Weekly team sync",
            due_date="2025-06-05",
            priority="medium",
            category="Work"
        )
        
        app.add_task(
            title="Doctor appointment",
            description="Annual checkup",
            due_date="2025-06-15",
            priority="high",
            category="Health"
        )
        
        # List all tasks
        print("\nAll tasks:")
        all_tasks = app.list_tasks()
        
        # Complete a task
        print("\nCompleting a task:")
        app.complete_task(all_tasks[2]["_id"])  # Complete the Morning jog
        
        # Update a task
        print("\nUpdating a task:")
        app.update_task(
            all_tasks[0]["_id"],  # Update the project proposal
            priority="high",
            due_date="2025-06-07"  # Changed from 2025-06-10
        )
        
        # Filter tasks
        print("\nHigh priority tasks:")
        app.list_tasks(priority="high")
        
        print("\nWork category tasks:")
        app.list_tasks(category="Work")
        
        print("\nTasks due this week (between 2025-06-03 and 2025-06-07):")
        app.list_tasks(due_after="2025-06-03", due_before="2025-06-07")
        
        # Show statistics
        app.get_stats()
        
        # Clean up - in a real app, you wouldn't drop the database
        print("\nCleaning up...")
        # Uncomment to clean up:
        # app.db.drop_db("todo_app")
        
    finally:
        # Stop the server
        print("\nStopping server...")
        server.stop()
    
    print("\nExample completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
