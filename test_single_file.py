#!/usr/bin/env python3
"""
Test loading a single SQL file with PostgreSQL compatibility
"""
import os
import psycopg2
import re

def convert_sqlite_to_postgresql(sql_content):
    """Convert SQLite SQL to PostgreSQL compatible SQL"""
    
    # Replace square brackets with double quotes for column names
    sql_content = re.sub(r'\[([^\]]+)\]', r'"\1"', sql_content)
    
    # Replace TEXT PRIMARY KEY with SERIAL PRIMARY KEY for auto-increment
    # But keep the id column as TEXT since the data has text IDs
    # sql_content = re.sub(r'id TEXT PRIMARY KEY', 'id SERIAL PRIMARY KEY', sql_content)
    
    # Handle SQLite specific syntax
    sql_content = sql_content.replace('TEXT NOT NULL', 'TEXT')
    sql_content = sql_content.replace('IF NOT EXISTS', '')
    
    return sql_content

def test_single_file():
    """Test loading one SQL file"""
    
    # Database connection
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    
    # Read test file
    test_file = "sql_chunks/authentic_hadiths_chunk_0000.sql"
    with open(test_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("Original SQL (first 500 chars):")
    print(sql_content[:500])
    print("\n" + "="*50 + "\n")
    
    # Convert SQLite to PostgreSQL
    converted_sql = convert_sqlite_to_postgresql(sql_content)
    print("Converted SQL (first 500 chars):")
    print(converted_sql[:500])
    
    # Drop table if exists and recreate
    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS authentic_hadiths CASCADE;")
            print("🧹 Dropped existing table")
            
        with conn.cursor() as cursor:
            cursor.execute(converted_sql)
        print("\n✅ SUCCESS: SQL file loaded successfully!")
        
        # Count rows
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM authentic_hadiths;")
            count = cursor.fetchone()[0]
            print(f"✅ Loaded {count} rows into authentic_hadiths table")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    test_single_file()
