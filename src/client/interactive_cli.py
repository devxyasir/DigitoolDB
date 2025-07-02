#!/usr/bin/env python3
"""
Interactive CLI for DigitoolDB - A beginner-friendly command-line interface
"""
import argparse
import cmd
import json
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.client.simple_api import SimpleDB


class DigitoolInteractiveCLI(cmd.Cmd):
    """Interactive command-line interface for DigitoolDB"""
    
    intro = """
    ╔═══════════════════════════════════════════════╗
    ║           Welcome to DigitoolDB CLI           ║
    ║                                               ║
    ║    Type 'help' to see available commands      ║
    ║    Type 'exit' or 'quit' to exit              ║
    ╚═══════════════════════════════════════════════╝
    """
    prompt = 'DigitoolDB> '
    
    def __init__(self):
        """Initialize the CLI"""
        super().__init__()
        self.db = SimpleDB(auto_connect=True)
        self.current_db = None
        self.current_collection = None
        
        # Check connection
        if not self.db.connected:
            print("Could not connect to DigitoolDB server. Is it running?")
            print("Start the server with 'digid' and try again.")
            sys.exit(1)
        
        # Update prompt
        self._update_prompt()
    
    def _update_prompt(self):
        """Update the command prompt to show current context"""
        if self.current_collection:
            self.prompt = f"DigitoolDB/{self.current_db}/{self.current_collection}> "
        elif self.current_db:
            self.prompt = f"DigitoolDB/{self.current_db}> "
        else:
            self.prompt = "DigitoolDB> "
    
    def do_use(self, arg):
        """
        Select a database to use.
        Usage: use <database_name>
        """
        if not arg:
            print("Please specify a database name.")
            return
        
        # Create database if it doesn't exist
        dbs = self.db.list_dbs()
        if arg not in dbs:
            print(f"Database '{arg}' doesn't exist. Creating it...")
            self.db.create_db(arg)
        
        self.current_db = arg
        self.current_collection = None
        print(f"Using database: {self.current_db}")
        self._update_prompt()
    
    def do_collection(self, arg):
        """
        Select a collection to use.
        Usage: collection <collection_name>
        """
        if not self.current_db:
            print("Please select a database first using 'use <database_name>'.")
            return
        
        if not arg:
            print("Please specify a collection name.")
            return
        
        # Create collection if it doesn't exist
        db_obj = self.db.db(self.current_db)
        collections = db_obj.list_collections()
        if arg not in collections:
            print(f"Collection '{arg}' doesn't exist. Creating it...")
            db_obj.create_collection(arg)
        
        self.current_collection = arg
        print(f"Using collection: {self.current_collection}")
        self._update_prompt()
    
    def do_insert(self, arg):
        """
        Insert a document into the current collection.
        Usage: insert {"name": "John", "age": 30}
        """
        if not self._check_collection():
            return
        
        try:
            document = json.loads(arg)
            collection = self.db.db(self.current_db).collection(self.current_collection)
            doc_id = collection.insert(document)
            print(f"Document inserted with ID: {doc_id}")
        except json.JSONDecodeError:
            print("Error: Invalid JSON. Document should be in valid JSON format.")
            print("Example: insert {\"name\": \"John\", \"age\": 30}")
        except Exception as e:
            print(f"Error inserting document: {str(e)}")
    
    def do_find(self, arg):
        """
        Find documents in the current collection.
        Usage: find [query]
        Examples:
          find                   - Find all documents
          find {"name": "John"}  - Find documents where name is John
        """
        if not self._check_collection():
            return
        
        query = {}
        if arg:
            try:
                query = json.loads(arg)
            except json.JSONDecodeError:
                print("Error: Invalid JSON query. Query should be in valid JSON format.")
                print("Example: find {\"name\": \"John\"}")
                return
        
        try:
            collection = self.db.db(self.current_db).collection(self.current_collection)
            results = collection.find(query)
            
            if not results:
                print("No documents found.")
                return
            
            print(f"Found {len(results)} document(s):")
            for i, doc in enumerate(results, 1):
                print(f"\n--- Document {i} ---")
                print(json.dumps(doc, indent=2))
            
            print(f"\nTotal: {len(results)} document(s)")
        except Exception as e:
            print(f"Error finding documents: {str(e)}")
    
    def do_update(self, arg):
        """
        Update documents in the current collection.
        Usage: update <query> <update>
        Example: update {"name": "John"} {"$set": {"age": 31}}
        """
        if not self._check_collection():
            return
        
        args = arg.strip().split(' ', 1)
        if len(args) != 2:
            print("Error: Both query and update are required.")
            print("Example: update {\"name\": \"John\"} {\"$set\": {\"age\": 31}}")
            return
        
        try:
            query = json.loads(args[0])
            update = json.loads(args[1])
            
            collection = self.db.db(self.current_db).collection(self.current_collection)
            count = collection.update(query, update)
            
            if count > 0:
                print(f"Updated {count} document(s).")
            else:
                print("No documents matched the query.")
        except json.JSONDecodeError:
            print("Error: Invalid JSON. Both query and update should be in valid JSON format.")
        except Exception as e:
            print(f"Error updating documents: {str(e)}")
    
    def do_delete(self, arg):
        """
        Delete documents from the current collection.
        Usage: delete <query>
        Example: delete {"name": "John"}
        """
        if not self._check_collection():
            return
        
        if not arg:
            print("Error: Query is required.")
            print("Example: delete {\"name\": \"John\"}")
            return
        
        try:
            query = json.loads(arg)
            
            # Confirm deletion
            confirm = input("Are you sure you want to delete matching documents? [y/N]: ")
            if confirm.lower() != 'y':
                print("Delete operation cancelled.")
                return
            
            collection = self.db.db(self.current_db).collection(self.current_collection)
            count = collection.delete(query)
            
            if count > 0:
                print(f"Deleted {count} document(s).")
            else:
                print("No documents matched the query.")
        except json.JSONDecodeError:
            print("Error: Invalid JSON. Query should be in valid JSON format.")
        except Exception as e:
            print(f"Error deleting documents: {str(e)}")
    
    def do_index(self, arg):
        """
        Create or manage indices.
        Usage: 
          index create <field>  - Create an index on field
          index drop <field>    - Drop an index
          index list            - List all indices
        """
        if not self._check_collection():
            return
        
        args = arg.strip().split()
        if not args:
            print("Error: Subcommand required (create, drop, or list).")
            return
        
        collection = self.db.db(self.current_db).collection(self.current_collection)
        
        if args[0] == 'create' and len(args) > 1:
            field = args[1]
            result = collection.create_index(field)
            if result:
                print(f"Created index on field: {field}")
            else:
                print(f"Failed to create index on field: {field}")
        
        elif args[0] == 'drop' and len(args) > 1:
            field = args[1]
            result = collection.drop_index(field)
            if result:
                print(f"Dropped index on field: {field}")
            else:
                print(f"Failed to drop index on field: {field}")
        
        elif args[0] == 'list':
            indices = collection.list_indices()
            if indices:
                print("Indices:")
                for field in indices:
                    print(f"  - {field}")
            else:
                print("No indices found.")
        
        else:
            print("Invalid subcommand. Use 'create', 'drop', or 'list'.")
    
    def do_databases(self, arg):
        """
        List all databases.
        Usage: databases
        """
        dbs = self.db.list_dbs()
        
        if dbs:
            print("Databases:")
            for db_name in dbs:
                if db_name == self.current_db:
                    print(f"  * {db_name} (current)")
                else:
                    print(f"  - {db_name}")
            print(f"Total: {len(dbs)} database(s)")
        else:
            print("No databases found.")
    
    def do_collections(self, arg):
        """
        List collections in the current database.
        Usage: collections
        """
        if not self.current_db:
            print("Please select a database first using 'use <database_name>'.")
            return
        
        db_obj = self.db.db(self.current_db)
        collections = db_obj.list_collections()
        
        if collections:
            print(f"Collections in '{self.current_db}':")
            for coll_name in collections:
                if coll_name == self.current_collection:
                    print(f"  * {coll_name} (current)")
                else:
                    print(f"  - {coll_name}")
            print(f"Total: {len(collections)} collection(s)")
        else:
            print(f"No collections found in database '{self.current_db}'.")
    
    def do_drop_db(self, arg):
        """
        Drop a database.
        Usage: drop_db <database_name>
        """
        if not arg:
            print("Please specify a database name.")
            return
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to drop database '{arg}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Drop operation cancelled.")
            return
        
        result = self.db.drop_db(arg)
        if result:
            print(f"Dropped database: {arg}")
            
            # Update current context if necessary
            if arg == self.current_db:
                self.current_db = None
                self.current_collection = None
                self._update_prompt()
        else:
            print(f"Failed to drop database: {arg}")
    
    def do_drop_collection(self, arg):
        """
        Drop a collection.
        Usage: drop_collection <collection_name>
        """
        if not self.current_db:
            print("Please select a database first using 'use <database_name>'.")
            return
        
        if not arg:
            print("Please specify a collection name.")
            return
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to drop collection '{arg}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Drop operation cancelled.")
            return
        
        result = self.db.db(self.current_db).drop_collection(arg)
        if result:
            print(f"Dropped collection: {arg}")
            
            # Update current context if necessary
            if arg == self.current_collection:
                self.current_collection = None
                self._update_prompt()
        else:
            print(f"Failed to drop collection: {arg}")
    
    def do_help(self, arg):
        """Show help for a command or list all commands"""
        if arg:
            # Help for a specific command
            super().do_help(arg)
        else:
            # Overview of all commands
            print("\nAvailable Commands:")
            print("------------------")
            print("use <db>            - Select a database to use")
            print("collection <name>    - Select a collection to use")
            print("insert <json>        - Insert a document")
            print("find [query]         - Find documents (all if no query)")
            print("update <query> <upd> - Update documents")
            print("delete <query>       - Delete documents")
            print("index ...            - Manage indices (create/drop/list)")
            print("databases            - List all databases")
            print("collections          - List collections in current database")
            print("drop_db <name>       - Drop a database")
            print("drop_collection <n>  - Drop a collection")
            print("clear                - Clear the screen")
            print("exit, quit           - Exit the program")
            print("\nFor more details on a command, type 'help <command>'")
    
    def do_exit(self, arg):
        """Exit the program"""
        print("Goodbye!")
        return True
    
    def do_quit(self, arg):
        """Exit the program"""
        return self.do_exit(arg)
    
    def do_clear(self, arg):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def default(self, line):
        """Handle unknown commands"""
        print(f"Unknown command: {line}")
        print("Type 'help' to see available commands.")
    
    def _check_collection(self):
        """Check if a database and collection are selected"""
        if not self.current_db:
            print("Please select a database first using 'use <database_name>'.")
            return False
        
        if not self.current_collection:
            print("Please select a collection first using 'collection <collection_name>'.")
            return False
        
        return True


def main():
    """
    Main entry point for the interactive CLI
    """
    parser = argparse.ArgumentParser(description='DigitoolDB Interactive CLI')
    parser.add_argument('--host', default='localhost', help='Server hostname')
    parser.add_argument('--port', type=int, default=27017, help='Server port')
    
    args = parser.parse_args()
    
    try:
        # Start the interactive CLI
        cli = DigitoolInteractiveCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
