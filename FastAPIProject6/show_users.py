#!/usr/bin/env python3
"""
Script to display all database tables and their structure
"""

from database import engine, Base
from sqlalchemy import inspect

def show_all_tables():
    """Display all tables in the database with their columns"""
    inspector = inspect(engine)
    
    print("🗄️ Database Tables Overview")
    print("=" * 50)
    
    # Get all table names
    table_names = inspector.get_table_names()
    
    if not table_names:
        print("❌ No tables found in database")
        return
    
    print(f"📊 Found {len(table_names)} tables:")
    print()
    
    # Display each table with its columns
    for table_name in sorted(table_names):
        print(f"\n🏷️  Table: {table_name}")
        print("-" * 40)
        
        # Get columns for this table
        columns = inspector.get_columns(table_name)
        
        if columns:
            for column in columns:
                column_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                print(f"  ├─ {column['name']}: {column_type} ({nullable})")
        else:
            print("  └─ No columns found")
    
    print("\n" + "=" * 50)
    print("✅ Database table analysis complete!")

if __name__ == "__main__":
    show_all_tables()
