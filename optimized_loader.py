#!/usr/bin/env python3
"""
Optimized Islamic Data Loader for Nahdlatul Ulama AI
Handles 15,675 SQL files efficiently with progress tracking and deduplication
"""

import os
import glob
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import re
from typing import List, Dict, Any, Set
import time
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedIslamicLoader:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.chunk_directory = Path("sql_chunks")
        self.progress_file = "loading_progress.json"
        self.batch_size = 50  # Process files in batches
        self.processed_files: Set[str] = set()
        self.created_tables: Set[str] = set()
        self.total_records = 0
        
        # Load previous progress if exists
        self.load_progress()
    
    def load_progress(self):
        """Load previous progress to resume loading."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                    self.processed_files = set(progress.get('processed_files', []))
                    self.created_tables = set(progress.get('created_tables', []))
                    self.total_records = progress.get('total_records', 0)
                    logger.info(f"Resumed from previous progress: {len(self.processed_files)} files processed")
            except Exception as e:
                logger.warning(f"Could not load progress: {e}")
    
    def save_progress(self):
        """Save current progress."""
        progress = {
            'processed_files': list(self.processed_files),
            'created_tables': list(self.created_tables),
            'total_records': self.total_records,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f)
    
    def get_connection(self):
        """Get database connection."""
        try:
            conn = psycopg2.connect(self.database_url)
            conn.autocommit = True
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_sql_files(self) -> List[Path]:
        """Get all SQL chunk files, excluding already processed ones."""
        all_files = list(self.chunk_directory.glob("*.sql"))
        remaining_files = [f for f in all_files if f.name not in self.processed_files]
        logger.info(f"Found {len(remaining_files)} remaining files out of {len(all_files)} total")
        return remaining_files
    
    def convert_sqlite_to_postgres(self, sql_content: str) -> str:
        """Convert SQLite syntax to PostgreSQL."""
        # Replace square brackets with double quotes
        sql_content = re.sub(r'\[([^\]]+)\]', r'"\1"', sql_content)
        
        # Convert AUTOINCREMENT to SERIAL
        sql_content = re.sub(r'INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY', sql_content)
        sql_content = re.sub(r'AUTOINCREMENT', '', sql_content)
        
        # Handle TEXT type
        sql_content = re.sub(r'\bTEXT\b', 'TEXT', sql_content)
        
        return sql_content
    
    def extract_table_name(self, sql_content: str) -> str:
        """Extract table name from CREATE TABLE statement."""
        match = re.search(r'CREATE TABLE (?:IF NOT EXISTS\s+)?["\']?([^"\'\s\(]+)["\']?', sql_content, re.IGNORECASE)
        if match:
            return match.group(1).strip('"\'')
        return ""
    
    def process_file(self, file_path: Path, conn) -> bool:
        """Process a single SQL file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.warning(f"Empty file: {file_path.name}")
                return False
            
            # Convert SQLite to PostgreSQL
            postgres_sql = self.convert_sqlite_to_postgres(content)
            
            # Extract table name
            table_name = self.extract_table_name(postgres_sql)
            if not table_name:
                logger.warning(f"Could not extract table name from {file_path.name}")
                return False
            
            # Split SQL into statements
            statements = [stmt.strip() for stmt in postgres_sql.split(';') if stmt.strip()]
            
            cursor = conn.cursor()
            records_added = 0
            
            for statement in statements:
                try:
                    if statement.upper().startswith('CREATE TABLE'):
                        # Check if table already exists
                        if table_name in self.created_tables:
                            logger.debug(f"Table {table_name} already exists, skipping CREATE")
                            continue
                        
                        cursor.execute(statement)
                        self.created_tables.add(table_name)
                        logger.debug(f"Created table: {table_name}")
                    
                    elif statement.upper().startswith('INSERT'):
                        cursor.execute(statement)
                        records_added += 1
                
                except psycopg2.IntegrityError as e:
                    if 'duplicate key' in str(e):
                        # Skip duplicate records silently
                        conn.rollback()
                        conn.autocommit = True
                        continue
                    else:
                        logger.error(f"Integrity error in {file_path.name}: {e}")
                        conn.rollback()
                        conn.autocommit = True
                        continue
                
                except Exception as e:
                    logger.error(f"Error executing statement in {file_path.name}: {e}")
                    conn.rollback()
                    conn.autocommit = True
                    continue
            
            cursor.close()
            self.total_records += records_added
            logger.debug(f"Processed {file_path.name}: {records_added} records added")
            return True
            
        except Exception as e:
            logger.error(f"Error processing file {file_path.name}: {e}")
            return False
    
    def load_all_chunks(self):
        """Load all SQL chunks with progress tracking."""
        logger.info("🕌 Starting optimized Islamic data loading...")
        
        sql_files = self.get_sql_files()
        if not sql_files:
            logger.info("✅ All files already processed!")
            return
        
        start_time = time.time()
        conn = self.get_connection()
        
        try:
            processed_count = 0
            batch_start = time.time()
            
            for i, file_path in enumerate(sql_files):
                if self.process_file(file_path, conn):
                    self.processed_files.add(file_path.name)
                    processed_count += 1
                
                # Progress update every batch
                if (i + 1) % self.batch_size == 0:
                    batch_time = time.time() - batch_start
                    total_processed = len(self.processed_files)
                    remaining = len(sql_files) - i - 1
                    eta = (remaining / self.batch_size) * batch_time if batch_time > 0 else 0
                    
                    logger.info(f"📊 Progress: {total_processed}/{len(sql_files) + len(self.processed_files)} files "
                              f"({(total_processed / (len(sql_files) + len(self.processed_files))) * 100:.1f}%) "
                              f"| Records: {self.total_records} | ETA: {eta/60:.1f}m")
                    
                    # Save progress periodically
                    self.save_progress()
                    batch_start = time.time()
            
            # Final save
            self.save_progress()
            
            total_time = time.time() - start_time
            logger.info(f"✅ Loading complete! Processed {processed_count} new files in {total_time/60:.1f} minutes")
            logger.info(f"📊 Total processed: {len(self.processed_files)} files, {self.total_records} records")
            
        except Exception as e:
            logger.error(f"Error during batch loading: {e}")
            self.save_progress()
            raise
        finally:
            conn.close()
    
    def get_statistics(self):
        """Get loading statistics."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get table list and counts
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cursor.fetchall()]
            
            table_stats = {}
            total_records = 0
            
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) as count FROM "{table}"')
                    result = cursor.fetchone()
                    count = result['count'] if result else 0
                    table_stats[table] = count
                    total_records += count
                except Exception as e:
                    logger.warning(f"Could not count table {table}: {e}")
                    table_stats[table] = 0
            
            cursor.close()
            return {
                'tables': len(tables),
                'total_records': total_records,
                'table_breakdown': table_stats,
                'processed_files': len(self.processed_files)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close()

def main():
    """Main function to run the optimized loader."""
    try:
        loader = OptimizedIslamicLoader()
        
        # Show current stats
        stats = loader.get_statistics()
        if stats:
            logger.info(f"📊 Current database state: {stats['tables']} tables, {stats['total_records']} records")
        
        # Load remaining data
        loader.load_all_chunks()
        
        # Show final stats
        final_stats = loader.get_statistics()
        if final_stats:
            logger.info(f"🏁 Final state: {final_stats['tables']} tables, {final_stats['total_records']} records")
            logger.info(f"📁 Processed {final_stats['processed_files']} files")
        
    except Exception as e:
        logger.error(f"Loading failed: {e}")
        raise

if __name__ == "__main__":
    main()
