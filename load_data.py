#!/usr/bin/env python3
"""
Nahdlatul Ulama AI - Data Loading Script
Load Islamic texts from SQL chunks into Railway PostgreSQL
"""

import os
import glob
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IslamicDataLoader:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")

        # Connect to Railway PostgreSQL
        self.conn = psycopg2.connect(self.db_url)
        self.conn.autocommit = True

    def create_tables(self):
        """Create necessary tables for Islamic texts"""
        with self.conn.cursor() as cursor:
            # Main Islamic texts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS islamic_texts (
                    id SERIAL PRIMARY KEY,
                    source_type VARCHAR(20) NOT NULL, -- quran, hadith, kitab
                    content TEXT NOT NULL,
                    arabic_text TEXT,
                    translation TEXT,
                    reference VARCHAR(100),
                    madhab VARCHAR(20) DEFAULT 'syafii',
                    authenticity VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_type ON islamic_texts(source_type);
                CREATE INDEX IF NOT EXISTS idx_madhab ON islamic_texts(madhab);
                CREATE INDEX IF NOT EXISTS idx_content_search ON islamic_texts USING gin(to_tsvector('arabic', content));
            """)

            logger.info("Tables created successfully")

    def load_sql_chunks(self, chunks_dir: str = "sql_chunks"):
        """Load all SQL chunks from directory"""
        if not os.path.exists(chunks_dir):
            logger.error(f"Directory {chunks_dir} not found")
            return

        sql_files = glob.glob(os.path.join(chunks_dir, "*.sql"))
        logger.info(f"Found {len(sql_files)} SQL chunk files")

        for sql_file in sorted(sql_files):
            try:
                self.load_single_chunk(sql_file)
                logger.info(f"Loaded {os.path.basename(sql_file)}")
            except Exception as e:
                logger.error(f"Error loading {sql_file}: {str(e)}")

    def load_single_chunk(self, sql_file: str):
        """Load a single SQL chunk file"""
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split SQL content into individual statements
        statements = self.split_sql_statements(sql_content)

        with self.conn.cursor() as cursor:
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        logger.warning(f"Skipping statement: {str(e)}")

    def split_sql_statements(self, sql: str) -> List[str]:
        """Split SQL content into individual statements"""
        statements = []
        current_statement = ""
        in_string = False
        string_char = None

        for char in sql:
            if char in ["'", '"'] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None

            current_statement += char

            if char == ';' and not in_string:
                statements.append(current_statement.strip())
                current_statement = ""

        if current_statement.strip():
            statements.append(current_statement.strip())

        return statements

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    source_type,
                    COUNT(*) as count,
                    madhab
                FROM islamic_texts
                GROUP BY source_type, madhab
                ORDER BY source_type, madhab;
            """)

            results = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) as total FROM islamic_texts;")
            total = cursor.fetchone()['total']

            return {
                "total_texts": total,
                "breakdown": results
            }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main data loading function"""
    loader = IslamicDataLoader()

    try:
        logger.info("Creating tables...")
        loader.create_tables()

        logger.info("Loading SQL chunks...")
        loader.load_sql_chunks()

        logger.info("Getting statistics...")
        stats = loader.get_stats()

        logger.info("Data loading completed!")
        logger.info(f"Total Islamic texts loaded: {stats['total_texts']}")

        for row in stats['breakdown']:
            logger.info(f"- {row['source_type']} ({row['madhab']}): {row['count']}")

    except Exception as e:
        logger.error(f"Data loading failed: {str(e)}")
        raise
    finally:
        loader.close()

if __name__ == "__main__":
    main()
