# Railway Deployment Guide for Nahdlatul Ulama AI

## Current Status
✅ **Fixed Issues:**
- Fixed `railway.toml` TOML syntax error
- Created separate Dockerfiles for web and Ollama services
- Updated Ollama port configuration (11434)
- Committed and pushed changes to trigger new deployment

## Railway Services Configuration

### 1. **Main Web Service** (Current failing service)
- **Name**: `nahdlatul-ulama-web`
- **Dockerfile**: `Dockerfile.web`
- **Port**: 8000
- **Environment Variables Needed**:
  ```
  PORT=8000
  OLLAMA_SERVICE_URL=http://ollama-qwen25-service:11434
  DATABASE_URL=postgresql://[auto-provided-by-railway]
  ```

### 2. **Ollama Service** (Create new service)
- **Name**: `ollama-qwen25-service`
- **Dockerfile**: `Dockerfile` (the existing one)
- **Port**: 11434
- **Memory**: 4GB minimum (for Qwen2.5-1.5B-Instruct)

### 3. **PostgreSQL Database** (Already created)
- ✅ Already deployed successfully

## Steps to Fix Current Deployment

### Step 1: Update Current Service
1. Go to your Railway project dashboard
2. Select the failing `ollama-qwen25-service`
3. Go to **Settings** → **Service Settings**
4. Change **Dockerfile Path** to `Dockerfile.web`
5. Rename service to `nahdlatul-ulama-web`

### Step 2: Create Ollama Service
1. Click **+ New Service**
2. Choose **GitHub Repo** → Select your repository
3. Name it `ollama-qwen25-service`
4. Set **Dockerfile Path** to `Dockerfile`
5. Set **Port** to `11434`
6. Increase **Memory** to 4GB

### Step 3: Set Environment Variables
For the web service, add these environment variables:
```
OLLAMA_SERVICE_URL=http://ollama-qwen25-service:11434
```

## Expected Architecture
```
┌─────────────────────────────────────────┐
│             Railway Project             │
├─────────────────────────────────────────┤
│  nahdlatul-ulama-web (port 8000)       │
│  ├── FastAPI application               │
│  ├── ChromaDB vector store             │
│  └── Connects to other services        │
├─────────────────────────────────────────┤
│  ollama-qwen25-service (port 11434)     │
│  ├── Ollama server                      │
│  ├── Qwen2.5-1.5B-Instruct model        │
│  └── Serves AI inference                │
├─────────────────────────────────────────┤
│  PostgreSQL Database                    │
│  ├── Islamic texts and hadiths         │
│  ├── User queries and responses         │
│  └── Scholar verification data          │
└─────────────────────────────────────────┘
```

## Test Endpoints After Deployment
1. **Health Check**: `GET /api/health`
2. **Root**: `GET /`
3. **Islamic Query**: `POST /api/islamic-query`

## Next Steps After Successful Deployment
1. Load SQL chunks into PostgreSQL database
2. Test Qwen2.5 model integration
3. Implement vector embeddings for Islamic texts
4. Add scholar verification workflow

The railway.toml syntax error has been fixed. Your next deployment should work correctly!
