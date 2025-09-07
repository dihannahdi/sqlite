# GitHub Copilot Instructions for Nahdlatul Ulama AI Project

## 🎯 Project Context

You are working on an **ultra-efficient** Islamic AI system that combines traditional Nahdlatul Ulama (NU) jurisprudence methodology with the most cost-effective and Railway-optimized AI technologies. The system implements **SmolLM2-360M** for local inference via **Ollama** on Railway, and includes a unique **Mushoheh verification layer** for Islamic scholarly validation.

## 🏗️ Ultra-Efficient Architecture Overview

```
User Query → SmolLM2-360M (Railway Ollama) → NU Methodology Engine → Mushoheh Verification → Verified Response
                ↑                           ↑                        ↑
         Railway RAG System          Rule-Based Reasoning         Scholar Review
         (ChromaDB on Railway)       (Bayani/Qiyasi/Istishlahi)  (Human Verification)
                ↑                           ↑                        ↑
         Railway PostgreSQL          Railway SQL Chunks          Railway Services
```

**Key Technologies:**
- **SmolLM2-360M-Instruct**: 374K downloads, 360M parameters, Railway-hosted
- **Ollama**: Containerized LLM serving on Railway
- **Railway**: PostgreSQL + Ollama service + Web service
- **Total Cost**: $20/month (Railway Pro plan only)

## 📚 Core Knowledge Base

### Islamic Jurisprudence (Fiqh) Fundamentals
- **Ahlussunnah wal Jama'ah (Aswaja)**: Traditional Sunni methodology
- **Four Madhabs**: Hanafi, Maliki, Syafi'i, Hambali (primarily Syafi'i for NU)
- **Istinbath Methods**: Bayani (textual), Qiyasi (analogical), Istishlahi/Maqashidi (benefit-based)

### NU's Four Core Principles (Fikrah Nahdliyah)
1. **Tawassuth** (Moderation): Avoid extremes, seek middle path
2. **Tasamuh** (Tolerance): Accept valid differences in jurisprudence 
3. **Tawazun** (Balance): Integrate religious and worldly considerations
4. **I'tidal** (Justice): Ensure fairness and righteousness

### Sources of Islamic Law (Adillah Syar'iyyah)
1. **Primary Sources**: Quran, Sunnah/Hadith
2. **Secondary Sources**: Ijma (consensus), Qiyas (analogy)
3. **Additional Sources**: Maslaha (public interest), Istihsan (juristic preference)

## 🔧 Technical Guidelines

### Code Style and Architecture

**Python Coding Standards for SmolLM2 Integration**:
```python
# Always use descriptive names for Islamic concepts
class SmolLMIslamicProcessor:
    def __init__(self):
        # Railway-hosted Ollama client
        self.ollama_url = os.getenv('OLLAMA_SERVICE_URL', 'http://ollama-smollm-service:8000')
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, Railway-hosted
        self.vector_db = chromadb.PersistentClient(path='/app/chroma_data')  # Railway persistent storage
    
    def process_islamic_query(self, query: str, context: str) -> IslamicResponse:
        """
        Process Islamic query with SmolLM2-360M via Railway Ollama.
        
        Args:
            query: Islamic question or topic
            context: Relevant Islamic sources (Quran, Hadith)
            
        Returns:
            IslamicResponse with NU methodology applied
        """
        prompt = f"""بسم الله الرحمن الرحيم

You are an Islamic AI assistant following Nahdlatul Ulama methodology.

Question: {query}
Context: {context}

Apply NU principles: Tawassuth (moderation), Tasamuh (tolerance), 
Tawazun (balance), and I'tidal (justice).

Answer:"""
        
        # Use SmolLM2 via Railway Ollama service
        response = requests.post(f"{self.ollama_url}/api/generate", json={
            "model": "SmolLM2-360M-Instruct",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 300,
                "num_ctx": 1024
            }
        })
        
        if response.status_code == 200:
            return IslamicResponse(
                answer=response.json()['response'],
                methodology='NU Islamic Jurisprudence',
                model_used='SmolLM2-360M-Instruct (Railway)',
                cost='Railway hosting only',
                verification_needed=True
            )
        else:
            raise Exception(f"Railway Ollama service failed: {response.status_code}")
**Railway Database Schema Conventions**:
```sql
-- Optimized for Railway PostgreSQL Pro plan
CREATE TABLE islamic_texts (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(20) NOT NULL, -- quran, hadith, kitab
    content TEXT NOT NULL,
    arabic_text TEXT,
    translation TEXT,
    reference VARCHAR(100),
    madhab VARCHAR(20) DEFAULT 'syafii',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Railway-optimized indexes
CREATE INDEX idx_source_type ON islamic_texts(source_type);
CREATE INDEX idx_madhab ON islamic_texts(madhab);
CREATE INDEX idx_content_search ON islamic_texts USING gin(to_tsvector('arabic', content));

-- Cache SmolLM2 responses for efficiency
CREATE TABLE ai_responses (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) UNIQUE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    model_used VARCHAR(50) DEFAULT 'SmolLM2-360M',
    confidence DECIMAL(3,2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### SmolLM2 + Ollama Integration Guidelines

**Pure Railway Model Deployment**:
```python
class SmolLMRailwayDeployment:
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_SERVICE_URL', 'http://ollama-smollm-service:8000')
        
    def generate_islamic_response(self, query: str, context: List[str]) -> str:
        """Generate response using SmolLM2 on Railway."""
        # Prepare prompt with Islamic greeting and context
        prompt = self.prepare_islamic_prompt(query, context)
        
        # Call Railway Ollama service
        response = requests.post(f"{self.ollama_url}/api/generate", json={
            "model": "SmolLM2-360M-Instruct",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 300,
                "num_ctx": 1024
            }
        })
        
        if response.status_code == 200:
            return self.post_process_islamic_response(response.json()['response'])
        else:
            raise Exception(f"Railway Ollama service failed: {response.status_code}")
    
    def prepare_islamic_prompt(self, query: str, context: List[str]) -> str:
        """Format prompt with proper Islamic etiquette."""
        return f"""بسم الله الرحمن الرحيم
In the name of Allah, the Most Gracious, the Most Merciful.

Question: {query}

Relevant Islamic Sources:
{chr(10).join(context)}

Please provide a response based on Nahdlatul Ulama methodology, considering:
1. Quran and Sunnah as primary sources
2. The four NU principles: Tawassuth, Tasamuh, Tawazun, I'tidal
3. Madhab Syafi'i jurisprudence when applicable
4. Classical Islamic scholarship traditions

Response:"""
```

### NU Methodology Implementation for Islamic Reasoning

**Hierarchical Reasoning Structure**:
```python
class NUMethodologyEngine:
    def __init__(self):
        self.rag_system = FreeIslamicRAG()
        self.methodology_rules = self.load_methodology_rules()
        
        # Question classification patterns
        self.question_patterns = {
            'worship': ['salah', 'prayer', 'sholat', 'ibadah', 'worship'],
            'commerce': ['jual', 'beli', 'dagang', 'business', 'trade'],
            'family': ['nikah', 'marriage', 'keluarga', 'family', 'divorce'],
            'social': ['muamalah', 'society', 'community', 'sosial'],
            'contemporary': ['technology', 'modern', 'kontemporer', 'new']
        }
        
    def perform_istinbath(self, question: str, sources: List[IslamicText]) -> ReasoningResult:
        """
        Implement Islamic legal reasoning (istinbath) using NU methodology.
        
        The method follows NU's three-tier approach:
        1. Bayani: Direct textual analysis
        2. Qiyasi: Analogical reasoning  
        3. Istishlahi: Benefit-consideration reasoning
        """
        
        # Determine appropriate reasoning method
        question_category = self.classify_question(question)
        primary_method = self.determine_istinbath_method(question, question_category)
        
        results = []
        if primary_method == "bayani":
            result = self.apply_bayani_method(question, sources)
        elif primary_method == "qiyasi":
            result = self.apply_qiyasi_method(question, sources)
        elif primary_method == "istishlahi":
            result = self.apply_istishlahi_method(question, sources)
                
        results.append(result)
        
        # Synthesize results using NU principles
        return self.synthesize_with_nu_principles(results)
    
    def apply_bayani_method(self, question: str, sources: List[IslamicText]) -> MethodologyResult:
        """Apply Bayani (textual analysis) method."""
        # Filter for direct textual sources (Quran, Sahih Hadith)
        primary_sources = [src for src in sources if src.source_type in ['quran', 'hadith']]
        
        reasoning = "Bayani Analysis: Direct textual analysis of Quran and Sunnah sources.\n"
        for source in primary_sources[:3]:
            reasoning += f"- {source.source_type.title()}: {source.text[:200]}...\n"
        
        # Apply NU principles: Tawassuth (moderation), I'tidal (justice)
        principles = ['tawassuth', 'itidal']
        confidence = sum([src.confidence for src in primary_sources]) / len(primary_sources) if primary_sources else 0.5
        
        return MethodologyResult(
            method='bayani',
            principles_applied=principles,
            reasoning=reasoning,
            confidence=confidence,
            requires_verification=confidence < 0.7
        )
```

### Free Islamic RAG System

**Retrieval Strategy**:
```python
class RailwayIslamicRAG:
    def __init__(self):
        self.smollm_processor = SmolLMIslamicProcessor()
        self.vector_store = chromadb.PersistentClient(path='/app/chroma_data')
        self.knowledge_graph = IslamicKnowledgeGraph()
        
    def retrieve_relevant_texts(self, query: str, madhab: str = "syafii") -> List[IslamicContext]:
        """
        Retrieve relevant Islamic texts with madhab and topic awareness.
        """
        
        # Stage 1: Semantic similarity search (Railway ChromaDB)
        query_embeddings = self.smollm_processor.embedding_model.encode(query).tolist()
        
        quran_results = self.smollm_processor.quran_collection.query(
            query_embeddings=[query_embeddings],
            n_results=2,
            where={'madhab': madhab} if madhab else None
        )
        
        # Stage 2: Hadith search with authenticity filter
        hadith_results = self.smollm_processor.hadith_collection.query(
            query_embeddings=[query_embeddings],
            n_results=1,
            where={'authenticity': {'$in': ['sahih', 'hasan']}}
        )
        
        # Stage 3: Rank by Islamic authority
        contexts = self.rank_by_islamic_authority(quran_results, hadith_results)
        
        return contexts[:5]  # Return top 5
    
    def rank_by_islamic_authority(self, quran_results, hadith_results) -> List[IslamicContext]:
        """Rank texts by Islamic scholarly authority and authenticity."""
        contexts = []
        
        # Quran has highest authority
        for i, doc in enumerate(quran_results['documents'][0]):
            contexts.append(IslamicContext(
                text=doc,
                source_type='quran',
                confidence=1.0 - quran_results['distances'][0][i],
                source_reference=f"Surah {quran_results['metadatas'][0][i]['surah']}"
            ))
        
        # Sahih hadith has very high authority
        for i, doc in enumerate(hadith_results['documents'][0]):
            contexts.append(IslamicContext(
                text=doc,
                source_type='hadith',
                confidence=0.9 - hadith_results['distances'][0][i],
                source_reference="Sahih Hadith Collection"
            ))
                
        return sorted(contexts, key=lambda x: x.confidence, reverse=True)
```

### Mushoheh Verification Layer

**Verification Workflow**:
```python
class MushohehVerificationSystem:
    def __init__(self):
        self.auto_verifier = AutomaticVerification()
        self.scholar_network = ScholarNetwork()
        self.verification_db = VerificationDatabase()
        
    def verify_islamic_response(self, 
                              question: str, 
                              response: str, 
                              sources: List[IslamicText]) -> VerificationResult:
        """
        Multi-stage verification following Islamic scholarly standards.
        """
        
        # Stage 1: Automatic verification
        auto_result = self.auto_verifier.verify(response, sources)
        
        if auto_result.confidence_score > 0.85:
            return VerificationResult(
                status="auto_verified",
                badge="🤖 AI-Verified",
                confidence=auto_result.confidence_score,
                notes="Automatic verification based on established sources"
            )
        
        # Stage 2: Route to appropriate scholar
        scholar_category = self.determine_scholar_category(question)
        assigned_scholar = self.scholar_network.assign_scholar(scholar_category)
        
        # Stage 3: Human verification
        human_result = assigned_scholar.review_response(question, response, sources)
        
        return VerificationResult(
            status="scholar_verified" if human_result.approved else "needs_revision",
            badge="✅ Verified by NU Scholar" if human_result.approved else "⚠️ [UNVERIFIED]",
            confidence=human_result.confidence,
            scholar_notes=human_result.notes,
            reviewer=assigned_scholar.name
        )
```

## 🌐 Database Integration Guidelines

### Railway Database Connection
```python
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class RailwayDatabase:
    def __init__(self):
        # Railway provides DATABASE_URL environment variable
        self.database_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def load_islamic_texts_batch(self, batch_size: int = 1000):
        """Load Islamic texts from chunked SQL files in batches."""
        session = self.SessionLocal()
        try:
            # Process GitHub SQL chunks
            for chunk_file in self.get_chunk_files():
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    
                # Execute SQL chunks safely
                session.execute(text(sql_content))
                session.commit()
                
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
```

### Knowledge Graph Integration
```python
import networkx as nx
from neo4j import GraphDatabase

class IslamicKnowledgeGraph:
    def __init__(self, neo4j_uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
        
    def create_islamic_entities(self, text: IslamicText):
        """Create knowledge graph entities for Islamic texts."""
        with self.driver.session() as session:
            # Create Quran verse node
            if text.source_type == "quran":
                session.run("""
                    CREATE (v:QuranVerse {
                        surah: $surah,
                        ayah: $ayah,
                        arabic_text: $arabic_text,
                        translation: $translation,
                        theme: $theme
                    })
                """, **text.to_dict())
            
            # Create Hadith node
            elif text.source_type == "hadith":
                session.run("""
                    CREATE (h:Hadith {
                        text: $text,
                        narrator_chain: $isnad,
                        authenticity: $authenticity,
                        source_book: $source_book
                    })
                """, **text.to_dict())
    
    def find_related_rulings(self, concept: str) -> List[str]:
        """Find related Islamic rulings for a given concept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $concept})-[:RELATES_TO]->(r:Ruling)
                RETURN r.text as ruling_text
            """, concept=concept)
            
            return [record["ruling_text"] for record in result]
```
            # Create Quran verse node
            if text.source_type == "quran":
                session.run("""
                    CREATE (v:QuranVerse {
                        surah: $surah,
                        ayah: $ayah,
                        arabic_text: $arabic_text,
                        translation: $translation,
                        theme: $theme
                    })
                """, **text.to_dict())
            
            # Create Hadith node
            elif text.source_type == "hadith":
                session.run("""
                    CREATE (h:Hadith {
                        text: $text,
                        narrator_chain: $isnad,
                        authenticity: $authenticity,
                        source_book: $source_book
                    })
                """, **text.to_dict())
    
    def find_related_rulings(self, concept: str) -> List[str]:
        """Find related Islamic rulings for a given concept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $concept})-[:RELATES_TO]->(r:Ruling)
                RETURN r.text as ruling_text
            """, concept=concept)
            
            return [record["ruling_text"] for record in result]
```

## 📝 Response Formatting Guidelines

### Islamic Response Structure
```python
def format_islamic_response(content: str, sources: List[IslamicText], verification: VerificationResult) -> str:
    """Format response according to Islamic etiquette and scholarly standards."""
    
    response = f"""
بسم الله الرحمن الرحيم

{verification.badge}

**الجواب (Answer):**

{content}

**الأدلة (Sources):**
"""
    
    for i, source in enumerate(sources, 1):
        response += f"\n{i}. {source.citation}"
        if source.arabic_text:
            response += f"\n   Arabic: {source.arabic_text}"
        if source.translation:
            response += f"\n   Translation: {source.translation}"
    
    response += f"""

**المنهج المتبع (Methodology Applied):**
- Nahdlatul Ulama traditional istinbath methodology
- Following Madhab Syafi'i jurisprudence
- Applying the four NU principles: Tawassuth, Tasamuh, Tawazun, I'tidal

{verification.scholar_notes if verification.scholar_notes else ""}

والله أعلم (And Allah knows best)
"""
    
    return response
```

## 🔍 Testing Guidelines

### Islamic Content Testing
```python
import pytest

class TestIslamicReasoning:
    def test_quran_verse_retrieval(self):
        """Test accurate Quran verse retrieval and citation."""
        retriever = IslamicRAGRetriever()
        
        # Test with known Quran verse
        results = retriever.retrieve_quran_verse(2, 255)  # Ayat Kursi
        
        assert len(results) == 1
        assert results[0].surah == 2
        assert results[0].ayah == 255
        assert "الله لا إله إلا هو الحي القيوم" in results[0].arabic_text
    
    def test_hadith_authenticity_filtering(self):
        """Test that only authentic hadith are used for reasoning."""
        retriever = IslamicRAGRetriever()
        
        results = retriever.retrieve_hadith(
            topic="prayer",
            authenticity_filter=["sahih", "hasan"]
        )
        
        for hadith in results:
            assert hadith.authenticity in ["sahih", "hasan"]
    
    def test_nu_principle_application(self):
        """Test that NU principles are properly applied."""
        reasoner = IslamicHierarchicalReasoning()
        
        # Test question that requires moderation (tawassuth)
        question = "What is the ruling on using technology in worship?"
        result = reasoner.perform_istinbath(question, [])
        
        assert "tawassuth" in result.principles_applied
        assert "moderate approach" in result.reasoning.lower()
```

## 🚨 Error Handling for Islamic Content

```python
class IslamicContentError(Exception):
    """Base exception for Islamic content processing errors."""
    pass

class QuranCitationError(IslamicContentError):
    """Raised when Quran citation is invalid."""
    def __init__(self, surah: int, ayah: int):
        self.message = f"Invalid Quran citation: Surah {surah}, Ayah {ayah}"
        super().__init__(self.message)

class HadithAuthenticityError(IslamicContentError):
    """Raised when hadith authenticity cannot be verified."""
    pass

# Usage in code
def validate_quran_reference(surah: int, ayah: int):
    """Validate Quran reference against known surah/ayah counts."""
    if not (1 <= surah <= 114):
        raise QuranCitationError(surah, ayah)
    
    # Check against known ayah counts per surah
    if ayah > SURAH_AYAH_COUNTS[surah]:
        raise QuranCitationError(surah, ayah)
```

## 📊 Performance Guidelines

### Optimization for Arabic Text Processing
```python
import functools
from typing import Dict, Any

@functools.lru_cache(maxsize=1000)
def cached_arabic_stemming(text: str) -> str:
    """Cache Arabic stemming results for better performance."""
    return arabic_stemmer.stem(text)

class OptimizedIslamicRAG:
    def __init__(self):
        self.embedding_cache: Dict[str, Any] = {}
        
    def get_cached_embedding(self, text: str) -> np.ndarray:
        """Use cached embeddings for frequently accessed Islamic texts."""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        if text_hash not in self.embedding_cache:
            self.embedding_cache[text_hash] = self.embedding_model.encode(text)
            
        return self.embedding_cache[text_hash]
```

## 🔐 Security and Privacy Guidelines

### Protecting Sacred Texts
```python
class SecureIslamicTextHandler:
    def __init__(self):
        self.encryption_key = os.getenv('ISLAMIC_TEXT_ENCRYPTION_KEY')
        
    def secure_store_quran_text(self, text: str) -> str:
        """Encrypt Quran text for secure storage."""
        # Use proper encryption for sacred texts
        cipher = Fernet(self.encryption_key)
        encrypted_text = cipher.encrypt(text.encode())
        return encrypted_text.decode()
    
    def validate_text_integrity(self, text: str, known_hash: str) -> bool:
        """Validate integrity of Islamic texts."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return text_hash == known_hash
```

## 📋 Code Review Checklist

Before submitting any code related to Islamic content:

- [ ] **Islamic Accuracy**: Verify all Quran verses and hadith citations
- [ ] **Arabic Text**: Ensure proper Arabic text encoding (UTF-8)
- [ ] **Scholarly Sources**: Validate all Islamic source attributions
- [ ] **NU Methodology**: Confirm adherence to NU principles
- [ ] **Respectful Language**: Use appropriate Islamic terminology
- [ ] **Error Handling**: Implement proper error handling for Islamic content
- [ ] **Performance**: Optimize for Arabic text processing
- [ ] **Testing**: Include Islamic content-specific tests
- [ ] **Documentation**: Document Islamic concepts clearly
- [ ] **Security**: Protect sacred texts appropriately

## 🚫 CRITICAL: File Management Guidelines

**JANGAN KEBIASAAN BIKIN FILE BARU HIH! JUST SEE WHAT'S ACTUALLY EXIST AND REFINE. DON'T ALWAYS NEW NEW NEW!**

### File Management Rules:
1. **ALWAYS check existing files first** - Use `read_file`, `list_dir`, `file_search` before creating anything
2. **REFINE, don't replace** - Use `replace_string_in_file` to update existing code
3. **Only create new files when absolutely necessary** - When existing files can't accommodate the changes
4. **Check imports and dependencies** - Ensure new code works with existing structure
5. **Respect the established architecture** - Don't reinvent what already exists

### Before Creating Any New File:
- [ ] Did I check what files already exist?
- [ ] Can I modify an existing file instead?
- [ ] Am I duplicating functionality that's already there?
- [ ] Did I read the existing code structure?
- [ ] Is this new file absolutely necessary?

**Remember: REFINEMENT > RECREATION**

## ⚡ Railway Deployment Optimization Results

### 🔥 Speed Improvements:

**Before Optimization:**
- Copying 15,674 SQL files during Docker build
- Large image size (>2GB)
- Build time: 15-30 minutes
- Slow layer caching

**After Optimization:**
- No SQL files copied during build (excluded via `.dockerignore`)
- Multi-stage build with dependency caching
- Build cache mounts for pip packages
- Minimal production image (~200MB)
- Build time: 2-3 minutes (10x faster!)

### 🏗️ How It Works Now:

1. **Build Stage**: Only copies essential files (`main.py`, `railway_rag.py`, `requirements.txt`)
2. **Production Stage**: Minimal runtime environment
3. **Runtime Download**: SQL files downloaded from GitHub API when needed
4. **Smart Caching**: Docker layers cached between deployments

### 📊 Performance Comparison:

```
⚡ OLD APPROACH:
├── Copy 15,674+ files during build: 15-20 min
├── Large Docker image: 2+ GB
├── Slow Railway deployment: 25-30 min total
└── Memory waste during build

🚀 NEW OPTIMIZED APPROACH:
├── Copy only 3 essential files: 30 seconds
├── Multi-stage cached build: 2-3 min
├── Fast Railway deployment: 3-5 min total  
└── Smart runtime data loading
```

### 🚀 Optimization Implementation Files:

- **`.dockerignore`**: Excludes sql_chunks/ from Docker build
- **`Dockerfile.web`**: Multi-stage build with cache mounts  
- **`railway.toml`**: Optimized build patterns and Docker BuildKit
- **`.env.railway`**: Performance environment variables

## 🤝 Collaboration Guidelines

### Working with Islamic Scholars
- Always prefix commits involving religious content with "REVIEW:" 
- Tag scholars for review on pull requests involving jurisprudence
- Use Islamic dates (Hijri) alongside Gregorian dates in documentation
- Include Arabic terms with English translations in comments

### Community Engagement
- Participate in Islamic AI ethics discussions
- Contribute to open-source Islamic NLP tools
- Share knowledge responsibly within Islamic academic communities
- Maintain highest standards of Islamic scholarly ethics

---

*These instructions should guide all development work on the Nahdlatul Ulama AI project. When in doubt about Islamic content or methodology, always consult with qualified Islamic scholars before proceeding.*
