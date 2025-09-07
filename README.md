# Nahdlatul Ulama AI - Islamic Jurisprudence System

بسم الله الرحمن الرحيم

An ultra-efficient Islamic AI system combining traditional Nahdlatul Ulama (NU) jurisprudence methodology with cost-effective Railway deployment using SmolLM2-360M.

## 🎯 Project Overview

This system implements:
- **SmolLM2-360M-Instruct**: 360M parameter model, Railway-hosted via Ollama
- **NU Methodology**: Ahlussunnah wal Jama'ah (Aswaja) principles
- **Railway Deployment**: PostgreSQL + Ollama service (~$20/month)
- **Mushoheh Verification**: Scholar validation layer

## 🏗️ Architecture

```
User Query → Web Interface → SmolLM2 (Ollama) → NU Methodology Engine → Mushoheh Verification → Response
                    ↓
         Railway PostgreSQL (Islamic Texts)
                    ↓
         ChromaDB Vector Store (Embeddings)
```

## 🚀 Quick Start

### 1. Prerequisites
- Railway CLI installed: `npm install -g @railway/cli`
- Railway account with Pro plan ($5/month)

### 2. Deploy to Railway

```bash
# Clone and setup
git clone <repository-url>
cd nahdlatul-ulama-ai

# Login to Railway
railway login

# Initialize project
railway init

# Add services
railway add -d postgres
railway add -s ollama-smollm-service

# Deploy
railway up
```

### 3. Load Islamic Data

```bash
# Load SQL chunks into database
python load_data.py
```

### 4. Access the Application

Once deployed, Railway will provide a URL. Open it in your browser to access the Islamic AI interface.

## 📚 NU Methodology Implementation

### Four Core Principles (Fikrah Nahdliyah)
1. **Tawassuth** (Moderation): Avoid extremes
2. **Tasamuh** (Tolerance): Accept valid differences
3. **Tawazun** (Balance): Integrate religious and worldly
4. **I'tidal** (Justice): Ensure fairness

### Istinbath Methods
- **Bayani**: Direct textual analysis (Quran, Hadith)
- **Qiyasi**: Analogical reasoning
- **Istishlahi**: Benefit-based reasoning

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: Railway PostgreSQL connection string
- `OLLAMA_SERVICE_URL`: Ollama service URL (auto-configured)
- `PORT`: Web service port (default: 8000)

### Model Configuration
- **Model**: SmolLM2-360M-Instruct
- **Temperature**: 0.3 (balanced responses)
- **Context Window**: 1024 tokens
- **Cost**: ~$20/month total Railway hosting

## 📁 Project Structure

```
nahdlatul-ulama-ai/
├── main.py                 # FastAPI application
├── load_data.py           # Data loading script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Ollama service container
├── start-ollama.sh      # Ollama startup script
├── railway.toml         # Railway configuration
├── index.html           # Web interface
├── sql_chunks/          # Islamic text chunks
├── references/          # NU methodology docs
└── .github/             # Copilot instructions
```

## 🗄️ Database Schema

### Islamic Texts Table
```sql
CREATE TABLE islamic_texts (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(20), -- quran, hadith, kitab
    content TEXT,
    arabic_text TEXT,
    translation TEXT,
    reference VARCHAR(100),
    madhab VARCHAR(20) DEFAULT 'syafii',
    authenticity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 API Endpoints

### POST `/api/islamic-query`
Process Islamic jurisprudence queries.

**Request:**
```json
{
    "question": "What is the ruling on using technology in worship?",
    "context": "Modern smartphone applications for prayer times",
    "madhab": "syafii"
}
```

**Response:**
```json
{
    "answer": "Islamic AI response...",
    "methodology": "NU Traditional Methodology",
    "sources": ["Quran 2:255", "Sahih Hadith"],
    "confidence": 0.85,
    "verification_status": "auto_verified"
}
```

### GET `/api/health`
Health check endpoint.

## 🧪 Testing

```bash
# Run tests
pytest

# Test API endpoints
curl -X POST http://localhost:8000/api/islamic-query \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## 📊 Performance

- **Model Size**: 360M parameters (2-4GB RAM)
- **Response Time**: < 3 seconds per query
- **Cost**: $20/month (Railway Pro plan)
- **Data**: 100+ Islamic text chunks loaded

## 🤝 Contributing

1. Follow NU methodology principles
2. Test with authentic Islamic sources
3. Ensure Arabic text compatibility
4. Add proper documentation

## 📜 License

This project is dedicated to Islamic scholarship and follows NU's commitment to Ahlussunnah wal Jama'ah.

## 🙏 Acknowledgments

- Nahdlatul Ulama organization
- Islamic scholars and ulema
- SmolLM2 and Ollama communities
- Railway platform

---

**والله أعلم** (And Allah knows best)

For questions or contributions, please contact the development team.
