#!/usr/bin/env python3

import requests
import time

def test_github_strategies():
    """Test multiple GitHub API strategies to handle large repositories."""
    
    repo = 'dihannahdi/sqlite'
    sql_chunks_path = 'sql_chunks'
    
    print("🚀 Testing Multiple GitHub API Strategies for Large Repositories\n")
    
    # Strategy 1: GitHub Search API
    print("=" * 60)
    print("🔍 Strategy 1: GitHub Search API")
    print("=" * 60)
    
    try:
        search_files = []
        page = 1
        per_page = 100  # Search API limit
        
        while True:
            search_url = "https://api.github.com/search/code"
            params = {
                'q': f'extension:sql repo:{repo} path:{sql_chunks_path}',
                'per_page': per_page,
                'page': page
            }
            
            print(f"🔍 Searching page {page}...")
            response = requests.get(search_url, params=params)
            
            if response.status_code == 403:
                print("⚠️ Rate limited")
                break
                
            if response.status_code == 422:
                print("⚠️ Query too complex")
                break
            
            response.raise_for_status()
            data = response.json()
            
            page_files = [item['name'] for item in data.get('items', []) 
                         if item['name'].endswith('.sql')]
            
            search_files.extend(page_files)
            print(f"📄 Page {page}: {len(page_files)} files (Total: {len(search_files)})")
            
            if len(page_files) < per_page or len(search_files) >= data.get('total_count', 0):
                break
                
            page += 1
            time.sleep(0.3)  # Be nice to GitHub
            
            if page > 5:  # Limit for testing
                break
        
        print(f"✅ Search API found: {len(search_files)} files")
        
    except Exception as e:
        print(f"❌ Search API failed: {e}")
        search_files = []
    
    # Strategy 2: Git Trees API (non-recursive)
    print("\n" + "=" * 60)
    print("🌳 Strategy 2: Git Trees API (non-recursive)")
    print("=" * 60)
    
    try:
        # Get repository info
        repo_url = f'https://api.github.com/repos/{repo}'
        repo_response = requests.get(repo_url)
        repo_response.raise_for_status()
        default_branch = repo_response.json()['default_branch']
        print(f"📋 Default branch: {default_branch}")
        
        # Get commit SHA
        branch_url = f'https://api.github.com/repos/{repo}/git/refs/heads/{default_branch}'
        branch_response = requests.get(branch_url)
        branch_response.raise_for_status()
        commit_sha = branch_response.json()['object']['sha']
        print(f"📝 Commit SHA: {commit_sha}")
        
        # Get root tree
        commit_url = f'https://api.github.com/repos/{repo}/git/commits/{commit_sha}'
        commit_response = requests.get(commit_url)
        commit_response.raise_for_status()
        root_tree_sha = commit_response.json()['tree']['sha']
        print(f"🌲 Root tree SHA: {root_tree_sha}")
        
        # Get root tree (non-recursive)
        tree_url = f'https://api.github.com/repos/{repo}/git/trees/{root_tree_sha}'
        tree_response = requests.get(tree_url)
        tree_response.raise_for_status()
        tree_data = tree_response.json()
        
        # Find sql_chunks directory
        sql_chunks_sha = None
        for item in tree_data['tree']:
            if item['path'] == sql_chunks_path and item['type'] == 'tree':
                sql_chunks_sha = item['sha']
                break
        
        if sql_chunks_sha:
            print(f"📁 Found {sql_chunks_path} directory: {sql_chunks_sha}")
            
            # Get sql_chunks tree
            chunks_tree_url = f'https://api.github.com/repos/{repo}/git/trees/{sql_chunks_sha}'
            chunks_response = requests.get(chunks_tree_url)
            chunks_response.raise_for_status()
            chunks_data = chunks_response.json()
            
            tree_files = [item['path'] for item in chunks_data['tree'] 
                         if item['type'] == 'blob' and item['path'].endswith('.sql')]
            
            print(f"✅ Git Trees found: {len(tree_files)} files")
            print(f"🔧 Tree truncated: {chunks_data.get('truncated', False)}")
        else:
            print(f"❌ {sql_chunks_path} directory not found")
            tree_files = []
        
    except Exception as e:
        print(f"❌ Git Trees failed: {e}")
        tree_files = []
    
    # Strategy 3: Contents API (fallback)
    print("\n" + "=" * 60)
    print("� Strategy 3: Contents API (fallback)")
    print("=" * 60)
    
    try:
        contents_url = f'https://api.github.com/repos/{repo}/contents/{sql_chunks_path}'
        print(f"📂 Trying Contents API: {contents_url}")
        
        response = requests.get(contents_url)
        
        if response.status_code == 403:
            print("❌ Rate limited")
            contents_files = []
        elif response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            contents_files = []
        else:
            files = response.json()
            contents_files = [f['name'] for f in files if f['name'].endswith('.sql')]
            print(f"✅ Contents API found: {len(contents_files)} files")
        
    except Exception as e:
        print(f"❌ Contents API failed: {e}")
        contents_files = []
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"🔍 Search API:    {len(search_files):,} files")
    print(f"🌳 Git Trees:     {len(tree_files):,} files")  
    print(f"📂 Contents API:  {len(contents_files):,} files")
    
    best_count = max(len(search_files), len(tree_files), len(contents_files))
    if best_count >= 15000:
        print(f"\n🎉 SUCCESS! Best method found {best_count:,} files!")
    elif best_count >= 1000:
        print(f"\n✅ GOOD! Found {best_count:,} files")
    else:
        print(f"\n⚠️ Limited success: {best_count:,} files")
    
    return {
        'search': search_files,
        'trees': tree_files,
        'contents': contents_files
    }

if __name__ == "__main__":
    results = test_github_strategies()
