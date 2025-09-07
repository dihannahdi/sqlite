#!/usr/bin/env python3
"""
Data Integrity Verification for Islamic Knowledge Base
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

class IslamicDataVerifier:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.conn = psycopg2.connect(self.db_url)
        self.conn.autocommit = True

    def get_all_tables(self):
        """Get list of all Islamic content tables"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            return [row[0] for row in cursor.fetchall()]

    def count_total_records(self):
        """Count total records across all tables"""
        tables = self.get_all_tables()
        total_count = 0
        table_counts = {}
        
        for table in tables:
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                    total_count += count
            except Exception as e:
                table_counts[table] = f"ERROR: {str(e)}"
        
        return total_count, table_counts

    def verify_arabic_content(self):
        """Verify Arabic text content integrity"""
        arabic_samples = []
        
        # Check authentic_hadiths table for Arabic content
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT hadith_text, narrator, hadith_source
                    FROM authentic_hadiths 
                    WHERE hadith_text IS NOT NULL 
                    LIMIT 5;
                """)
                results = cursor.fetchall()
                
                for row in results:
                    # Check for Arabic characters (Unicode range)
                    has_arabic = any('\u0600' <= char <= '\u06FF' for char in row['hadith_text'])
                    arabic_samples.append({
                        'text_sample': row['hadith_text'][:100] + "..." if len(row['hadith_text']) > 100 else row['hadith_text'],
                        'has_arabic': has_arabic,
                        'narrator': row['narrator'],
                        'source': row['hadith_source']
                    })
        except Exception as e:
            arabic_samples.append({'error': f"Failed to verify Arabic content: {str(e)}"})
        
        return arabic_samples

    def check_data_quality(self):
        """Check data quality and completeness"""
        quality_report = {
            'timestamp': datetime.now().isoformat(),
            'database_connection': 'SUCCESS',
            'tables_found': 0,
            'total_records': 0,
            'table_breakdown': {},
            'arabic_content_samples': [],
            'data_quality_issues': []
        }
        
        try:
            # Count tables and records
            total_count, table_counts = self.count_total_records()
            quality_report['tables_found'] = len(table_counts)
            quality_report['total_records'] = total_count
            quality_report['table_breakdown'] = table_counts
            
            # Verify Arabic content
            arabic_samples = self.verify_arabic_content()
            quality_report['arabic_content_samples'] = arabic_samples
            
            # Check for potential issues
            if total_count == 0:
                quality_report['data_quality_issues'].append("WARNING: No records found in database")
            
            if total_count < 1000:
                quality_report['data_quality_issues'].append(f"WARNING: Only {total_count} records found - expected 500K+")
            
            # Check for empty tables
            empty_tables = [table for table, count in table_counts.items() if isinstance(count, int) and count == 0]
            if empty_tables:
                quality_report['data_quality_issues'].append(f"WARNING: Empty tables found: {empty_tables}")
            
        except Exception as e:
            quality_report['database_connection'] = f'FAILED: {str(e)}'
            quality_report['data_quality_issues'].append(f"CRITICAL: Database connection failed: {str(e)}")
        
        return quality_report

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        report = self.check_data_quality()
        
        print("=" * 60)
        print("🕌 ISLAMIC KNOWLEDGE BASE - DATA INTEGRITY REPORT")
        print("=" * 60)
        print(f"📅 Generated: {report['timestamp']}")
        print(f"🔗 Database: {report['database_connection']}")
        print()
        
        print("📊 DATABASE STATISTICS:")
        print(f"   Tables Found: {report['tables_found']}")
        print(f"   Total Records: {report['total_records']:,}")
        print()
        
        if report['table_breakdown']:
            print("📋 TABLE BREAKDOWN:")
            for table, count in sorted(report['table_breakdown'].items()):
                if isinstance(count, int):
                    print(f"   {table}: {count:,} records")
                else:
                    print(f"   {table}: {count}")
            print()
        
        if report['arabic_content_samples']:
            print("🔤 ARABIC CONTENT VERIFICATION:")
            for i, sample in enumerate(report['arabic_content_samples'][:3], 1):
                if 'error' in sample:
                    print(f"   Sample {i}: {sample['error']}")
                else:
                    print(f"   Sample {i}:")
                    print(f"      Text: {sample['text_sample']}")
                    print(f"      Arabic: {'✅ YES' if sample['has_arabic'] else '❌ NO'}")
                    print(f"      Narrator: {sample.get('narrator', 'N/A')}")
                    print(f"      Source: {sample.get('source', 'N/A')}")
                    print()
        
        if report['data_quality_issues']:
            print("⚠️  DATA QUALITY ISSUES:")
            for issue in report['data_quality_issues']:
                print(f"   {issue}")
            print()
        
        # Overall status
        if report['total_records'] > 10000 and not report['data_quality_issues']:
            print("✅ OVERALL STATUS: EXCELLENT - Islamic knowledge base is ready!")
        elif report['total_records'] > 1000:
            print("🟡 OVERALL STATUS: GOOD - Some data loaded, may need more processing")
        else:
            print("🔴 OVERALL STATUS: NEEDS ATTENTION - Insufficient data loaded")
        
        print("=" * 60)
        return report

def main():
    """Main verification function"""
    try:
        verifier = IslamicDataVerifier()
        report = verifier.generate_summary_report()
        
        # Save detailed report to JSON
        with open('data_integrity_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Detailed report saved to: data_integrity_report.json")
        
    except Exception as e:
        print(f"❌ VERIFICATION FAILED: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
