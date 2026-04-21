#!/usr/bin/env python
"""
Database Inspection Script for Academic ERP System
Run this script to explore your complete database structure and data.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.apps import apps

def show_all_tables():
    """Show all tables in the database"""
    print("=" * 60)
    print("ALL TABLES IN DATABASE")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        for i, (table_name,) in enumerate(tables, 1):
            print(f"{i:2d}. {table_name}")
    
    print(f"\nTotal tables: {len(tables)}")
    return [table[0] for table in tables]

def show_table_structure(table_name):
    """Show structure of a specific table"""
    print(f"\n{'=' * 60}")
    print(f"STRUCTURE OF TABLE: {table_name}")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        print(f"{'Field':<25} {'Type':<20} {'Null':<5} {'Key':<5} {'Default':<10} {'Extra'}")
        print("-" * 80)
        
        for column in columns:
            field, type_, null, key, default, extra = column
            print(f"{field:<25} {type_:<20} {null:<5} {key:<5} {str(default):<10} {extra}")

def show_table_data(table_name, limit=5):
    """Show sample data from a table"""
    print(f"\n{'=' * 60}")
    print(f"SAMPLE DATA FROM: {table_name} (First {limit} rows)")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        if rows:
            # Get column names
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [col[0] for col in cursor.fetchall()]
            
            # Print header
            header = " | ".join(f"{col[:15]:<15}" for col in columns)
            print(header)
            print("-" * len(header))
            
            # Print data
            for row in rows:
                row_str = " | ".join(f"{str(val)[:15]:<15}" for val in row)
                print(row_str)
        else:
            print("No data found in this table.")

def show_django_models():
    """Show all Django models and their relationships"""
    print("\n" + "=" * 60)
    print("DJANGO MODELS AND RELATIONSHIPS")
    print("=" * 60)
    
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('apps.'):  # Only our custom apps
            print(f"\nApp: {app_config.name}")
            print("-" * 40)
            
            for model in app_config.get_models():
                print(f"  Model: {model.__name__}")
                print(f"    Table: {model._meta.db_table}")
                
                # Show fields
                fields = []
                for field in model._meta.fields:
                    field_info = f"{field.name} ({field.__class__.__name__})"
                    if hasattr(field, 'related_model') and field.related_model:
                        field_info += f" -> {field.related_model.__name__}"
                    fields.append(field_info)
                
                if fields:
                    print(f"    Fields: {', '.join(fields[:3])}{'...' if len(fields) > 3 else ''}")
                
                print()

def count_records_in_all_tables():
    """Count records in all tables"""
    print("\n" + "=" * 60)
    print("RECORD COUNTS IN ALL TABLES")
    print("=" * 60)
    
    tables = show_all_tables()
    
    print(f"\n{'Table Name':<35} {'Record Count':<15}")
    print("-" * 50)
    
    with connection.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:<35} {count:<15}")
            except Exception as e:
                print(f"{table:<35} Error: {str(e)[:20]}")

def show_recent_registrations():
    """Show recent semester registrations with approval status"""
    print("\n" + "=" * 60)
    print("RECENT SEMESTER REGISTRATIONS")
    print("=" * 60)
    
    from apps.students.models import SemesterRegistration
    
    registrations = SemesterRegistration.objects.select_related(
        'student__user', 'approved_by'
    ).order_by('-created_at')[:10]
    
    if registrations:
        print(f"{'ID':<5} {'Student':<20} {'Academic Year':<12} {'Status':<10} {'Approved By':<15}")
        print("-" * 70)
        
        for reg in registrations:
            student_name = reg.student.user.get_full_name() or reg.student.user.username
            approved_by = reg.approved_by.username if reg.approved_by else 'N/A'
            
            print(f"{reg.id:<5} {student_name[:19]:<20} {reg.academic_year:<12} "
                  f"{reg.approval_status:<10} {approved_by[:14]:<15}")
    else:
        print("No registrations found.")

def main():
    """Main function to run database inspection"""
    print("ACADEMIC ERP DATABASE INSPECTION")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. Show all tables")
        print("2. Show Django models")
        print("3. Count records in all tables")
        print("4. Show table structure")
        print("5. Show table data")
        print("6. Show recent registrations")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            show_all_tables()
        
        elif choice == '2':
            show_django_models()
        
        elif choice == '3':
            count_records_in_all_tables()
        
        elif choice == '4':
            table_name = input("Enter table name: ").strip()
            if table_name:
                show_table_structure(table_name)
        
        elif choice == '5':
            table_name = input("Enter table name: ").strip()
            if table_name:
                limit = input("Enter number of rows to show (default 5): ").strip()
                limit = int(limit) if limit.isdigit() else 5
                show_table_data(table_name, limit)
        
        elif choice == '6':
            show_recent_registrations()
        
        elif choice == '7':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()