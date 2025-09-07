#!/usr/bin/env python3
"""
Railway-based Islamic RAG System
High-Performance Optimized Version for Fast Ingestion + Efficient Serving
"""

import os
import requests
import re
import logging
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import deque
import asyncio
import aiohttp
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import psutil
from tqdm import tqdm

# Try to import ghapi for better GitHub API handling
try:
    from ghapi.all import GhApi, paged
    GHAPI_AVAILABLE = True
except ImportError:
    GHAPI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class IslamicText:
    text: str
    source_type: str  # 'hadith', 'quran', 'book'
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

@dataclass  
class PerformanceConfig:
    """Configuration for high-performance ingestion vs efficient serving."""
    # Ingestion mode: Use all available resources
    ingestion_workers: int = min(32, (psutil.cpu_count() or 4) * 2)  # 2x CPU cores
    ingestion_batch_size: int = 100  # Large batches for speed
    ingestion_memory_limit: float = 0.8  # Use 80% of available RAM
    
    # Serving mode: Minimal resource usage
    serving_workers: int = 2
    serving_batch_size: int = 10
    serving_memory_limit: float = 0.3  # Use only 30% of RAM
    
    # Adaptive settings
    max_concurrent_downloads: int = 50
    embedding_batch_size: int = 64  # Process embeddings in large batches
    cache_size: int = 10000  # Cache frequently accessed items

class OptimizedRailwayIslamicRAG:
    def __init__(self, ingestion_mode: bool = False):
        """Initialize Railway-based Islamic RAG system with performance optimization."""
        # Performance configuration
        self.config = PerformanceConfig()
        self.ingestion_mode = ingestion_mode
        self.is_ingesting = False
        
        # Set resource limits based on mode
        if ingestion_mode:
            logger.info("🚀 INGESTION MODE: Using maximum resources for fast processing")
            self.workers = self.config.ingestion_workers
            self.batch_size = self.config.ingestion_batch_size
        else:
            logger.info("⚡ SERVING MODE: Using minimal resources for efficient serving")
            self.workers = self.config.serving_workers
            self.batch_size = self.config.serving_batch_size
        
        # GitHub repository configuration
        self.github_repo = "dihannahdi/sqlite"
        self.github_branch = "main"
        self.sql_chunks_path = "sql_chunks"
        
        # Railway storage paths
        self.embeddings_path = "/app/embeddings"
        self.chroma_path = "/app/chroma_data"
        
        # Thread-safe caches for performance
        self._file_cache = {}
        self._embedding_cache = {}
        self._cache_lock = threading.Lock()
        
        # Performance monitoring
        self.processed_files = 0
        self.start_time = None
        
        # Initialize embedding model (lightweight for Railway)
        logger.info("🤖 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB for Railway
        logger.info("📚 Initializing vector database...")
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create collections
        self.collections = {
            'hadith': self.chroma_client.get_or_create_collection("hadith_collection"),
            'quran': self.chroma_client.get_or_create_collection("quran_collection"),
            'islamic_books': self.chroma_client.get_or_create_collection("islamic_books_collection")
        }
        
        self.processed_files_set = set()
        self.total_documents = 0
    
    def get_github_file_list(self) -> List[str]:
        """Get list of SQL chunk files from GitHub repository using multiple strategies for large directories."""
        
        # Strategy 1: Try ghapi with pagination (if available)
        if GHAPI_AVAILABLE:
            logger.info("🚀 Attempting GitHub API with ghapi library...")
            files = self._get_files_with_ghapi()
            if files:
                return files
        
        # Strategy 2: Use GitHub Search API (handles large repos well)
        logger.info("🔍 Attempting GitHub Search API...")
        files = self._get_files_with_search_api()
        if files:
            return files
        
        # Strategy 3: Use Git Trees API with non-recursive approach
        logger.info("🌳 Attempting Git Trees API (non-recursive)...")
        files = self._get_files_with_git_trees()
        if files:
            return files
        
        # Strategy 4: Fallback to Contents API (limited to 1000 files)
        logger.info("📂 Fallback to Contents API...")
        return self._fallback_contents_api()
    
    def _get_files_with_ghapi(self) -> List[str]:
        """Use ghapi library for robust GitHub API access with automatic pagination."""
        try:
            api = GhApi()
            
            # Get repository contents for sql_chunks directory
            # Note: ghapi automatically handles pagination and rate limiting
            contents = api.repos.get_content(
                owner=self.github_repo.split('/')[0],
                repo=self.github_repo.split('/')[1], 
                path=self.sql_chunks_path
            )
            
            sql_files = []
            if isinstance(contents, list):
                sql_files = [item.name for item in contents if item.name.endswith('.sql')]
            
            logger.info(f"✅ ghapi found {len(sql_files)} SQL files")
            return sql_files
            
        except Exception as e:
            logger.error(f"❌ ghapi method failed: {e}")
            return []
    
    def _get_files_with_search_api(self) -> List[str]:
        """Use GitHub Search API to find SQL files (handles large repos well)."""
        try:
            all_sql_files = []
            page = 1
            per_page = 100  # Search API max is 100
            
            while True:
                search_url = "https://api.github.com/search/code"
                params = {
                    'q': f'extension:sql repo:{self.github_repo} path:{self.sql_chunks_path}',
                    'per_page': per_page,
                    'page': page
                }
                
                logger.info(f"🔍 Searching page {page}...")
                response = requests.get(search_url, params=params)
                
                if response.status_code == 403:
                    logger.warning("⚠️ Search API rate limited")
                    break
                
                if response.status_code == 422:
                    logger.warning("⚠️ Search API query too complex or rate limited")
                    break
                
                response.raise_for_status()
                data = response.json()
                
                page_files = [item['name'] for item in data.get('items', []) 
                             if item['name'].endswith('.sql')]
                
                all_sql_files.extend(page_files)
                logger.info(f"📄 Page {page}: {len(page_files)} files (Total: {len(all_sql_files)})")
                
                # Check if we've reached the end
                if len(page_files) < per_page or len(all_sql_files) >= data.get('total_count', 0):
                    break
                    
                page += 1
                time.sleep(0.2)  # Respect rate limits
            
            logger.info(f"✅ Search API found {len(all_sql_files)} SQL files")
            return all_sql_files
            
        except Exception as e:
            logger.error(f"❌ Search API failed: {e}")
            return []
    
    def _get_files_with_git_trees(self) -> List[str]:
        """Use Git Trees API with a non-recursive approach to avoid 7MB limit."""
        try:
            # Get the repository's default branch
            repo_url = f"https://api.github.com/repos/{self.github_repo}"
            repo_response = requests.get(repo_url)
            repo_response.raise_for_status()
            default_branch = repo_response.json()['default_branch']
            
            # Get the commit SHA
            branch_url = f"https://api.github.com/repos/{self.github_repo}/git/refs/heads/{default_branch}"
            branch_response = requests.get(branch_url)
            branch_response.raise_for_status()
            commit_sha = branch_response.json()['object']['sha']
            
            # Get the root tree
            commit_url = f"https://api.github.com/repos/{self.github_repo}/git/commits/{commit_sha}"
            commit_response = requests.get(commit_url)
            commit_response.raise_for_status()
            root_tree_sha = commit_response.json()['tree']['sha']
            
            # Get the root tree (non-recursive)
            tree_url = f"https://api.github.com/repos/{self.github_repo}/git/trees/{root_tree_sha}"
            tree_response = requests.get(tree_url)
            tree_response.raise_for_status()
            tree_data = tree_response.json()
            
            # Find the sql_chunks directory
            sql_chunks_sha = None
            for item in tree_data['tree']:
                if item['path'] == self.sql_chunks_path and item['type'] == 'tree':
                    sql_chunks_sha = item['sha']
                    break
            
            if not sql_chunks_sha:
                logger.error(f"❌ {self.sql_chunks_path} directory not found")
                return []
            
            # Get the sql_chunks directory tree (non-recursive)
            chunks_tree_url = f"https://api.github.com/repos/{self.github_repo}/git/trees/{sql_chunks_sha}"
            chunks_response = requests.get(chunks_tree_url)
            chunks_response.raise_for_status()
            chunks_data = chunks_response.json()
            
            # Extract SQL files
            sql_files = [item['path'] for item in chunks_data['tree'] 
                        if item['type'] == 'blob' and item['path'].endswith('.sql')]
            
            logger.info(f"✅ Git Trees found {len(sql_files)} SQL files")
            
            if chunks_data.get('truncated', False):
                logger.warning("⚠️ Tree response was truncated - some files may be missing")
            
            return sql_files
            
        except Exception as e:
            logger.error(f"❌ Git Trees API failed: {e}")
            return []
    
    def _fallback_contents_api(self) -> List[str]:
        """Fallback method using Contents API for smaller directories."""
        try:
            api_url = f"https://api.github.com/repos/{self.github_repo}/contents/{self.sql_chunks_path}"
            
            logger.info(f"🔍 Using Contents API fallback: {api_url}")
            response = requests.get(api_url)
            
            if response.status_code == 403:
                logger.error("❌ Rate limited on Contents API as well")
                return []
            
            response.raise_for_status()
            files = response.json()
            
            # GitHub returns an error if directory has >1000 files, but let's try anyway
            sql_files = [f['name'] for f in files if f['name'].endswith('.sql')]
            
            logger.info(f"📁 Fallback found {len(sql_files)} SQL files")
            return sql_files
            
        except Exception as e:
            logger.error(f"❌ Fallback method also failed: {e}")
            return []
    
    def get_github_file_content(self, filename: str) -> Optional[str]:
        """Get content of a specific SQL chunk file from GitHub."""
        try:
            raw_url = f"https://raw.githubusercontent.com/{self.github_repo}/{self.github_branch}/{self.sql_chunks_path}/{filename}"
            
            response = requests.get(raw_url)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Error fetching {filename}: {e}")
            return None
    
    def parse_sql_content_to_islamic_texts(self, sql_content: str, filename: str) -> List[IslamicText]:
        """Parse SQL content and convert to IslamicText objects."""
        documents = self.parse_sql_content(sql_content, filename)
        
        islamic_texts = []
        for doc in documents:
            # Determine source type based on doc_type
            source_type = self._map_doc_type_to_source(doc['doc_type'])
            
            islamic_text = IslamicText(
                text=doc['content'],
                source_type=source_type,
                metadata={
                    'source_table': doc['source_table'],
                    'source_file': doc['source_file'],
                    'doc_type': doc['doc_type'],
                    'id': doc['id'],
                    **doc['metadata']
                }
            )
            islamic_texts.append(islamic_text)
        
        return islamic_texts
    
    def _map_doc_type_to_source(self, doc_type: str) -> str:
        """Map document type to source type for collections."""
        if 'hadith' in doc_type.lower():
            return 'hadith'
        elif 'quran' in doc_type.lower() or 'ayat' in doc_type.lower():
            return 'quran'
        else:
            return 'islamic_books'

    def parse_sql_content(self, sql_content: str, filename: str) -> List[Dict[str, Any]]:
        """Parse SQL content to extract Islamic text documents."""
        documents = []
        
        try:
            # Extract table name
            table_match = re.search(r'CREATE TABLE ["\']?([^"\'\s\(]+)["\']?', sql_content, re.IGNORECASE)
            table_name = table_match.group(1) if table_match else filename.replace('.sql', '')
            
            # Find all INSERT statements
            insert_pattern = r'INSERT INTO.*?VALUES\s*\((.*?)\);'
            matches = re.findall(insert_pattern, sql_content, re.DOTALL | re.IGNORECASE)
            
            for i, match in enumerate(matches):
                try:
                    # Parse VALUES content
                    values = self.parse_insert_values(match)
                    
                    if values and len(values) > 1:
                        # Determine document type and extract content
                        doc_type = self.determine_document_type(table_name, values)
                        content = self.extract_content(values, doc_type)
                        
                        if content and len(content.strip()) > 10:  # Filter out empty/short content
                            document = {
                                'id': f"{table_name}_{i}",
                                'content': content,
                                'source_table': table_name,
                                'source_file': filename,
                                'doc_type': doc_type,
                                'metadata': self.extract_metadata(values, doc_type)
                            }
                            documents.append(document)
                
                except Exception as e:
                    logger.debug(f"Error parsing insert in {filename}: {e}")
                    continue
            
            logger.debug(f"📄 Extracted {len(documents)} documents from {filename}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error parsing SQL content from {filename}: {e}")
            return []
    
    def parse_insert_values(self, values_str: str) -> List[str]:
        """Parse INSERT VALUES string into individual values."""
        # Simple CSV-style parsing for VALUES content
        # Handle quoted strings with potential commas inside
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        i = 0
        while i < len(values_str):
            char = values_str[i]
            
            if not in_quotes and char in ['"', "'"]:
                in_quotes = True
                quote_char = char
                current_value += char
            elif in_quotes and char == quote_char:
                # Check if it's an escaped quote
                if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                    current_value += char + char
                    i += 1  # Skip next quote
                else:
                    in_quotes = False
                    quote_char = None
                    current_value += char
            elif not in_quotes and char == ',':
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        # Add last value
        if current_value.strip():
            values.append(current_value.strip())
        
        # Clean up values (remove quotes)
        cleaned_values = []
        for value in values:
            cleaned = value.strip()
            if cleaned.startswith('"') and cleaned.endswith('"'):
                cleaned = cleaned[1:-1]
            elif cleaned.startswith("'") and cleaned.endswith("'"):
                cleaned = cleaned[1:-1]
            cleaned_values.append(cleaned)
        
        return cleaned_values
    
    def determine_document_type(self, table_name: str, values: List[str]) -> str:
        """Determine the type of Islamic document."""
        table_lower = table_name.lower()
        
        if 'hadith' in table_lower:
            return 'hadith'
        elif 'quran' in table_lower or 'qur' in table_lower:
            return 'quran'
        else:
            return 'islamic_book'
    
    def extract_content(self, values: List[str], doc_type: str) -> str:
        """Extract main content from VALUES based on document type."""
        if not values:
            return ""
        
        if doc_type == 'hadith':
            # For hadith, content is usually in 2nd column (hadith_text)
            return values[1] if len(values) > 1 else values[0]
        else:
            # For other documents, content is usually in 2nd column
            return values[1] if len(values) > 1 else values[0]
    
    def extract_metadata(self, values: List[str], doc_type: str) -> Dict[str, Any]:
        """Extract metadata from VALUES based on document type."""
        metadata = {}
        
        try:
            if doc_type == 'hadith' and len(values) >= 6:
                metadata = {
                    'narrator': values[2] if len(values) > 2 else '',
                    'source': values[3] if len(values) > 3 else '',
                    'authenticity': values[4] if len(values) > 4 else '',
                    'topic': values[5] if len(values) > 5 else ''
                }
            else:
                metadata = {
                    'part': values[2] if len(values) > 2 else '',
                    'page': values[3] if len(values) > 3 else '',
                    'number': values[4] if len(values) > 4 else ''
                }
        except Exception as e:
            logger.debug(f"Error extracting metadata: {e}")
        
        return metadata
    
    def add_to_vector_db(self, documents: List[Dict[str, Any]]):
        """Add documents to appropriate vector database collection."""
        for doc in documents:
            try:
                collection_name = doc['doc_type']
                if collection_name not in self.collections:
                    collection_name = 'islamic_books'
                
                collection = self.collections[collection_name]
                
                # Create embedding
                embedding = self.embedding_model.encode(doc['content'])
                
                # Add to ChromaDB
                collection.add(
                    embeddings=[embedding.tolist()],
                    documents=[doc['content']],
                    metadatas=[{
                        'source_table': doc['source_table'],
                        'source_file': doc['source_file'],
                        'doc_type': doc['doc_type'],
                        **doc['metadata']
                    }],
                    ids=[doc['id']]
                )
                
                self.total_documents += 1
                
            except Exception as e:
                logger.error(f"❌ Error adding document {doc['id']} to vector DB: {e}")
    
    def process_file_from_github(self, filename: str) -> bool:
        """Process a single SQL chunk file from GitHub."""
        if filename in self.processed_files_set:
            return True
        
        try:
            logger.debug(f"📥 Processing {filename}...")
            
            # Get file content from GitHub
            content = self.get_github_file_content(filename)
            if not content:
                return False
            
            # Parse SQL content
            documents = self.parse_sql_content(content, filename)
            if not documents:
                logger.debug(f"⚠️ No documents extracted from {filename}")
                return True  # Not an error, just empty
            
            # Add to vector database
            self.add_to_vector_db(documents)
            
            self.processed_files_set.add(filename)
            logger.debug(f"✅ Processed {filename}: {len(documents)} documents")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {filename}: {e}")
            return False
    
    def build_rag_system(self, max_files: Optional[int] = None):
        """Build the complete RAG system from GitHub SQL chunks."""
        logger.info("🕌 Building Islamic RAG system from GitHub repository...")
        
        # Get list of files from GitHub
        sql_files = self.get_github_file_list()
        if not sql_files:
            logger.error("❌ No SQL files found on GitHub")
            return False
        
        # Limit files for testing if specified
        if max_files:
            sql_files = sql_files[:max_files]
            logger.info(f"📊 Processing first {max_files} files for testing")
        
        # Process files
        start_time = time.time()
        processed_count = 0
        
        for i, filename in enumerate(sql_files):
            if self.process_file_from_github(filename):
                processed_count += 1
            
            # Progress update every 50 files
            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                logger.info(f"📊 Progress: {i+1}/{len(sql_files)} files | "
                          f"Documents: {self.total_documents} | "
                          f"Time: {elapsed/60:.1f}m")
        
        logger.info(f"✅ RAG system built! Processed {processed_count} files, {self.total_documents} documents")
        return True
    
    def search(self, query: str, collection_type: str = 'all', n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the Islamic knowledge base."""
        try:
            query_embedding = self.embedding_model.encode(query)
            
            all_results = []
            
            if collection_type == 'all':
                collections_to_search = self.collections.values()
            else:
                collections_to_search = [self.collections.get(collection_type)]
                if not collections_to_search[0]:
                    logger.error(f"❌ Collection {collection_type} not found")
                    return []
            
            for collection in collections_to_search:
                try:
                    results = collection.query(
                        query_embeddings=[query_embedding.tolist()],
                        n_results=n_results
                    )
                    
                    for i, (doc, metadata, distance) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0],
                        results['distances'][0]
                    )):
                        all_results.append({
                            'content': doc,
                            'metadata': metadata,
                            'similarity': 1 - distance,
                            'rank': i + 1
                        })
                
                except Exception as e:
                    logger.error(f"❌ Error searching collection: {e}")
            
            # Sort by similarity and return top results
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            return all_results[:n_results]
            
        except Exception as e:
            logger.error(f"❌ Error during search: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        stats = {
            'total_documents': self.total_documents,
            'processed_files': len(self.processed_files_set),
            'collections': {}
        }
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats['collections'][name] = count
            except Exception as e:
                stats['collections'][name] = f"Error: {e}"
        
        return stats

    # ================= HIGH-PERFORMANCE OPTIMIZED METHODS =================
    
    async def fast_ingest_all_files(self) -> Dict[str, int]:
        """High-performance ingestion of all SQL files using asyncio and multithreading."""
        if not self.ingestion_mode:
            logger.warning("⚠️ Not in ingestion mode! Use OptimizedRailwayIslamicRAG(ingestion_mode=True)")
            return {}
        
        self.is_ingesting = True
        self.start_time = time.time()
        
        # Get file list
        logger.info("🔍 Discovering all SQL files...")
        sql_files = self.get_github_file_list()
        total_files = len(sql_files)
        
        if total_files == 0:
            logger.error("❌ No SQL files found!")
            return {}
        
        logger.info(f"📁 Found {total_files:,} SQL files to process")
        
        # Process files in optimized batches
        results = {'hadith': 0, 'quran': 0, 'islamic_books': 0}
        
        # Create progress bar
        with tqdm(total=total_files, desc="🚀 Fast Ingestion") as pbar:
            # Process in batches for memory efficiency
            batch_size = self.config.ingestion_batch_size
            
            for i in range(0, total_files, batch_size):
                batch_files = sql_files[i:i + batch_size]
                batch_results = await self._process_batch_async(batch_files)
                
                # Update results
                for source_type, count in batch_results.items():
                    results[source_type] += count
                
                # Update progress
                pbar.update(len(batch_files))
                self.processed_files += len(batch_files)
                
                # Memory management
                self._cleanup_memory_if_needed()
                
                # Log progress
                elapsed = time.time() - self.start_time
                rate = self.processed_files / elapsed if elapsed > 0 else 0
                pbar.set_postfix({
                    'rate': f'{rate:.1f} files/sec',
                    'memory': f'{psutil.virtual_memory().percent:.1f}%'
                })
        
        self.is_ingesting = False
        elapsed = time.time() - self.start_time
        
        logger.info(f"✅ INGESTION COMPLETE!")
        logger.info(f"📊 Processed {self.processed_files:,} files in {elapsed:.1f}s")
        logger.info(f"⚡ Average rate: {self.processed_files/elapsed:.1f} files/sec")
        logger.info(f"📈 Results: {results}")
        
        return results

    async def _process_batch_async(self, batch_files: List[str]) -> Dict[str, int]:
        """Process a batch of files asynchronously with high concurrency."""
        results = {'hadith': 0, 'quran': 0, 'islamic_books': 0}
        
        # Create semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)
        
        # Download files concurrently
        async with aiohttp.ClientSession() as session:
            download_tasks = [
                self._download_and_process_file_async(session, semaphore, filename)
                for filename in batch_files
            ]
            
            batch_texts = await asyncio.gather(*download_tasks, return_exceptions=True)
        
        # Filter successful results
        valid_texts = [text for text in batch_texts if isinstance(text, list)]
        all_texts = [text for sublist in valid_texts for text in sublist]
        
        if not all_texts:
            return results
        
        # Batch process embeddings
        await self._batch_process_embeddings(all_texts)
        
        # Count by source type
        for text in all_texts:
            results[text.source_type] += 1
        
        return results

    async def _download_and_process_file_async(self, session: aiohttp.ClientSession, 
                                             semaphore: asyncio.Semaphore, 
                                             filename: str) -> List[IslamicText]:
        """Download and process a single file asynchronously."""
        async with semaphore:
            try:
                # Check cache first
                with self._cache_lock:
                    if filename in self._file_cache:
                        return self._file_cache[filename]
                
                # Download file content
                file_url = f"https://raw.githubusercontent.com/{self.github_repo}/{self.github_branch}/{self.sql_chunks_path}/{filename}"
                
                async with session.get(file_url) as response:
                    if response.status != 200:
                        logger.warning(f"⚠️ Failed to download {filename}: HTTP {response.status}")
                        return []
                    
                    content = await response.text()
                
                # Process SQL content
                texts = self.parse_sql_content_to_islamic_texts(content, filename)
                
                # Cache result
                with self._cache_lock:
                    if len(self._file_cache) < self.config.cache_size:
                        self._file_cache[filename] = texts
                
                return texts
                
            except Exception as e:
                logger.error(f"❌ Error processing {filename}: {e}")
                return []

    async def _batch_process_embeddings(self, texts: List[IslamicText]):
        """Process embeddings in optimized batches."""
        if not texts:
            return
        
        # Process embeddings in batches
        batch_size = self.config.embedding_batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Extract text content
            text_content = [text.text for text in batch]
            
            # Generate embeddings in batch (much faster)
            embeddings = self.embedding_model.encode(
                text_content,
                batch_size=len(text_content),
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            # Assign embeddings back to texts
            for text, embedding in zip(batch, embeddings):
                text.embedding = embedding
            
            # Store in vector database
            await self._store_batch_in_vectordb(batch)

    async def _store_batch_in_vectordb(self, texts: List[IslamicText]):
        """Store a batch of texts in the vector database efficiently."""
        if not texts:
            return
        
        # Group by source type for efficient storage
        by_source = {'hadith': [], 'quran': [], 'islamic_books': []}
        
        for text in texts:
            if text.source_type in by_source:
                by_source[text.source_type].append(text)
        
        # Store each source type
        for source_type, source_texts in by_source.items():
            if source_texts:
                collection = self.collections[source_type]
                
                # Prepare batch data
                ids = [f"{source_type}_{i}_{hash(text.text)}" for i, text in enumerate(source_texts)]
                documents = [text.text for text in source_texts]
                embeddings = [text.embedding.tolist() for text in source_texts]
                metadatas = [text.metadata for text in source_texts]
                
                # Batch insert
                collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )

    def _cleanup_memory_if_needed(self):
        """Clean up memory if usage is too high."""
        memory_percent = psutil.virtual_memory().percent
        limit = self.config.ingestion_memory_limit * 100
        
        if memory_percent > limit:
            logger.warning(f"⚠️ Memory usage {memory_percent:.1f}% > {limit:.1f}%, cleaning cache...")
            
            with self._cache_lock:
                # Clear half of the cache
                cache_size = len(self._file_cache)
                if cache_size > 0:
                    items_to_remove = list(self._file_cache.keys())[:cache_size // 2]
                    for key in items_to_remove:
                        del self._file_cache[key]
                
                # Clear embedding cache
                self._embedding_cache.clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info(f"🧹 Memory cleaned, usage now: {psutil.virtual_memory().percent:.1f}%")

    def switch_to_serving_mode(self):
        """Switch from ingestion mode to efficient serving mode."""
        if self.ingestion_mode:
            logger.info("🔄 Switching to SERVING MODE for efficient queries...")
            self.ingestion_mode = False
            self.workers = self.config.serving_workers
            self.batch_size = self.config.serving_batch_size
            
            # Clear caches to free memory
            with self._cache_lock:
                self._file_cache.clear()
                self._embedding_cache.clear()
            
            logger.info("⚡ Now in serving mode - minimal resource usage")

# Alias for backward compatibility
RailwayIslamicRAG = OptimizedRailwayIslamicRAG

# Import time for timing
import time

def main():
    """Main function to build and test the RAG system."""
    try:
        # Initialize RAG system
        rag = RailwayIslamicRAG()
        
        # Build RAG system (test with first 100 files)
        success = rag.build_rag_system(max_files=100)
        
        if success:
            # Show statistics
            stats = rag.get_statistics()
            logger.info(f"📊 RAG Statistics: {json.dumps(stats, indent=2)}")
            
            # Test search
            test_query = "What is prayer in Islam?"
            logger.info(f"🔍 Testing search: '{test_query}'")
            
            results = rag.search(test_query, n_results=3)
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}: Similarity {result['similarity']:.3f}")
                logger.info(f"Content: {result['content'][:200]}...")
                logger.info(f"Metadata: {result['metadata']}")
                logger.info("---")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    main()
