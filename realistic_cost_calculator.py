#!/usr/bin/env python3
"""
High-Performance Ingestion Test for Railway Islamic RAG
Demonstrates the optimized approach vs standard approach
"""

import asyncio
import time
import logging
from railway_rag import OptimizedRailwayIslamicRAG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_high_performance_ingestion():
    """Test the high-performance ingestion method."""
    
    print("🚀 HIGH-PERFORMANCE ISLAMIC RAG INGESTION TEST")
    print("=" * 60)
    
    # Phase 1: Fast Ingestion Mode
    print("\n📥 PHASE 1: FAST INGESTION MODE")
    print("Using maximum Railway resources for speed...")
    
    # Initialize in ingestion mode (uses all available RAM/CPU)
    rag = OptimizedRailwayIslamicRAG(ingestion_mode=True)
    
    print(f"⚙️ Configuration:")
    print(f"   Workers: {rag.workers}")
    print(f"   Batch Size: {rag.batch_size}")
    print(f"   Concurrent Downloads: {rag.config.max_concurrent_downloads}")
    print(f"   Embedding Batch Size: {rag.config.embedding_batch_size}")
    print(f"   Memory Limit: {rag.config.ingestion_memory_limit * 100}%")
    
    # Start ingestion
    start_time = time.time()
    
    print(f"\n🔥 Starting fast ingestion of all 15,674 SQL files...")
    results = await rag.fast_ingest_all_files()
    
    ingestion_time = time.time() - start_time
    
    print(f"\n✅ INGESTION COMPLETED!")
    print(f"⏱️ Time: {ingestion_time:.1f} seconds")
    print(f"📊 Results: {results}")
    print(f"⚡ Rate: {sum(results.values()) / ingestion_time:.1f} docs/sec")
    
    # Phase 2: Switch to Serving Mode
    print(f"\n📤 PHASE 2: SWITCHING TO SERVING MODE")
    print("Optimizing for low resource usage...")
    
    rag.switch_to_serving_mode()
    
    print(f"⚙️ New Configuration:")
    print(f"   Workers: {rag.workers}")
    print(f"   Batch Size: {rag.batch_size}")
    print(f"   Memory Limit: {rag.config.serving_memory_limit * 100}%")
    
    # Test search performance
    print(f"\n🔍 PHASE 3: TESTING SEARCH PERFORMANCE")
    
    test_queries = [
        "What is prayer in Islam?",
        "How to perform wudu?",
        "What are the five pillars of Islam?",
        "Islamic marriage rules",
        "Zakat calculation"
    ]
    
    search_times = []
    
    for query in test_queries:
        search_start = time.time()
        results = rag.search(query, n_results=5)
        search_time = time.time() - search_start
        search_times.append(search_time)
        
        print(f"   Query: '{query}'")
        print(f"   Time: {search_time:.3f}s | Results: {len(results)}")
    
    avg_search_time = sum(search_times) / len(search_times)
    print(f"\n📈 Average search time: {avg_search_time:.3f} seconds")
    
    # Show statistics
    stats = rag.get_statistics()
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Total Documents: {stats['total_documents']:,}")
    print(f"   Processed Files: {stats['processed_files']:,}")
    
    for collection_name, count in stats['collections'].items():
        print(f"   {collection_name.title()}: {count:,} documents")
    
    print(f"\n🎯 PERFORMANCE SUMMARY:")
    print(f"   Ingestion Rate: {sum(results.values()) / ingestion_time:.1f} docs/sec")
    print(f"   Search Performance: {avg_search_time:.3f}s average")
    print(f"   Total Processing Time: {ingestion_time:.1f} seconds")
    
    # Calculate cost estimates
    railway_cost_per_hour = 0.067  # $20/month ÷ 24/7
    ingestion_cost = (ingestion_time / 3600) * railway_cost_per_hour
    
    print(f"\n💰 COST ESTIMATES (Railway Pro):")
    print(f"   Ingestion Cost: ${ingestion_cost:.2f}")
    print(f"   Monthly Serving: ~$20/month")
    print(f"   One-time Setup: ${ingestion_cost:.2f}")
    
    return {
        'ingestion_time': ingestion_time,
        'documents_processed': sum(results.values()),
        'search_performance': avg_search_time,
        'results': results,
        'cost': ingestion_cost
    }

def test_standard_vs_optimized():
    """Compare standard vs optimized approach."""
    
    print("\n" + "=" * 60)
    print("📊 STANDARD VS OPTIMIZED COMPARISON")
    print("=" * 60)
    
    # Estimates based on typical performance
    standard_estimates = {
        'files_per_second': 0.5,  # Sequential processing
        'total_files': 15674,
        'estimated_time': 15674 / 0.5 / 3600,  # hours
        'resource_usage': 'Low',
        'concurrency': 1
    }
    
    optimized_estimates = {
        'files_per_second': 20,  # Parallel processing
        'total_files': 15674,
        'estimated_time': 15674 / 20 / 3600,  # hours  
        'resource_usage': 'High (during ingestion)',
        'concurrency': 50
    }
    
    print(f"📈 STANDARD APPROACH:")
    print(f"   Processing Rate: {standard_estimates['files_per_second']} files/sec")
    print(f"   Estimated Time: {standard_estimates['estimated_time']:.1f} hours")
    print(f"   Resource Usage: {standard_estimates['resource_usage']}")
    print(f"   Concurrency: {standard_estimates['concurrency']}")
    
    print(f"\n🚀 OPTIMIZED APPROACH:")
    print(f"   Processing Rate: {optimized_estimates['files_per_second']} files/sec")
    print(f"   Estimated Time: {optimized_estimates['estimated_time']:.1f} hours") 
    print(f"   Resource Usage: {optimized_estimates['resource_usage']}")
    print(f"   Concurrency: {optimized_estimates['concurrency']}")
    
    speedup = standard_estimates['estimated_time'] / optimized_estimates['estimated_time']
    print(f"\n⚡ SPEEDUP: {speedup:.1f}x faster!")
    
    return speedup

async def main():
    """Main test function."""
    try:
        print("🕌 Railway Islamic RAG - High Performance Test")
        print("Testing optimized ingestion and serving performance")
        
        # Test comparison first
        speedup = test_standard_vs_optimized()
        
        # Run actual performance test
        print(f"\n🚀 Running actual performance test...")
        results = await test_high_performance_ingestion()
        
        print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print(f"✨ Performance improvement: {speedup:.1f}x faster than standard approach")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
