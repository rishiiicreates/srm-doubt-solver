# 🎓 OODP RAG Project - SRM College Doubt-Solving Agent

**Built by:** rishiicreates and friends  
**Portfolio:** https://my-portfolio-drab-nu-83.vercel.app/

---

## 📋 Overview

A RAG-based AI agent that answers student questions based on the official SRM college syllabus. Built with Streamlit, LangChain, Ollama (Llama 3), and ChromaDB.

**Purpose:** Help SRM students get accurate, syllabus-aligned answers to their academic doubts with proper citations.

---

## 🏗️ Architecture

### Core Components

#### 1. Frontend (`app.py`)
- Streamlit chat UI with modern glassmorphic design
- Real-time streaming responses
- Source citations with similarity scores
- Theme toggle (light/dark mode)
- Floating particle animations
- Semester and subject filters (currently disabled for global search)

#### 2. Knowledge Base (`generate_syllabus_kb.py`)
- 40+ subjects across 8 semesters
- Pre-structured syllabus topics per unit
- Covers CSE, ECE, Mech, BioTech, Physics, Chemistry, and more
- Each subject has detailed unit breakdowns with key concepts

#### 3. Ingestion Pipeline (`ingest.py`)
- Scrapes syllabus PPTs from thehelpers.vercel.app
- Downloads and processes PDF/PPT files from `data/` folder
- Chunks content (200 tokens, 30 overlap)
- Generates embeddings via Ollama (nomic-embed-text)
- Stores in ChromaDB vector store with metadata

#### 4. Retriever (`retriever.py`)
- Semantic search with ChromaDB
- Metadata filtering (semester, subject)
- Similarity threshold: 0.45
- Precision filtering (gap filter + subject isolation)
- Returns top-k chunks with full citations

#### 5. LLM Engine (`llm.py`)
- Query rewriting for better retrieval
- Context-aware prompt building
- Ollama Llama 3 (temperature: 0.3, context: 4096)
- Response caching with DiskCache (24h TTL)
- Streaming token generation

---

## 🛠️ Tech Stack

### Core Framework
- **LangChain** 0.3.20+
- **LangChain Community** 0.3.19+
- **LangChain Ollama** 0.3.2+

### Vector Store
- **ChromaDB** 0.6.3+
- **Embeddings:** nomic-embed-text (via Ollama)

### LLM
- **Ollama** (localhost:11434)
- **Model:** Llama 3

### Frontend
- **Streamlit** 1.42.0+

### Document Processing
- **unstructured** 0.16.20+
- **python-pptx** 1.0.2+
- **PyPDFLoader** (for PDFs)

### Web Scraping
- **requests** 2.32.3+
- **BeautifulSoup4** 4.12.3+
- **lxml** 5.3.0+
- **gdown** 5.2.0 (Google Drive downloads)

### Utilities
- **diskcache** 5.6.3 (response caching)
- **tiktoken** 0.8.0 (tokenization)
- **pydantic** 2.10.0+
- **numpy** 2.0.0+

---

## 🔄 How It Works

### User Query Flow

```
1. Student asks question via chat UI
        ↓
2. Query gets rewritten for better retrieval
   (resolves pronouns, adds subject context)
        ↓
3. Retriever searches ChromaDB with filters
   (semester, subject if selected)
        ↓
4. Top-k chunks retrieved (similarity > 0.45)
   Precision filter removes irrelevant results
        ↓
5. Context + system prompt sent to Llama 3
        ↓
6. Response streamed back with citations
        ↓
7. Result cached for 24 hours
```

### Ingestion Pipeline Flow

```
1. Scrape semester URLs from thehelpers.vercel.app
        ↓
2. Download PPT/PDF files to data/
        ↓
3. Load documents (per-slide/per-element granularity)
        ↓
4. Extract metadata (subject, semester, unit, URL)
        ↓
5. Chunk documents (200 tokens, 30 overlap)
        ↓
6. Generate embeddings via Ollama
        ↓
7. Store in ChromaDB with metadata
```

---

## 📁 Project Structure

```
oodp rag project/
├── app.py                    # Streamlit UI (1.1k lines)
├── config.py                 # All configuration constants
├── ingest.py                 # Ingestion pipeline
├── retriever.py              # Vector search logic
├── llm.py                    # LLM + caching + query rewrite
├── generate_syllabus_kb.py   # Syllabus knowledge base (40+ subjects)
├── requirements.txt          # Python dependencies
├── README.md                 # Project readme
├── site_data_manifest.json   # Scraped URL manifest
├── utils/
│   ├── downloader.py         # Web scraper + manifest loader
│   ├── chunker.py            # Text chunking with token counting
│   ├── metadata_extractor.py # Metadata parsing from paths
│   └── __init__.py
├── data/                     # Downloaded PPTs/PDFs
├── vectorstore/              # ChromaDB persistence directory
├── .response_cache/          # DiskCache storage
└── venv/                     # Python virtualenv
```

---

## ⚙️ Configuration (config.py)

### Ollama Settings
```python
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3"
EMBEDDING_MODEL = "nomic-embed-text"
```

### Chunking Settings
```python
CHUNK_SIZE = 200          # target tokens per chunk
CHUNK_OVERLAP = 30        # token overlap between chunks
MAX_CHUNK_TOKENS = 300    # hard ceiling
```

### Retrieval Settings
```python
TOP_K = 5
SIMILARITY_THRESHOLD = 0.45
EMBEDDING_BATCH_SIZE = 32
```

### Caching
```python
CACHE_TTL_SECONDS = 86400  # 24 hours
```

### Scraping
```python
HELPERS_BASE_URL = "https://thehelpers.vercel.app/"
TOTAL_SEMESTERS = 8
REQUEST_DELAY_SECONDS = 1.0
MAX_RETRIES = 3
```

### LLM Parameters
```python
LLM_TEMPERATURE = 0.3
LLM_NUM_CTX = 4096
```

---

## 🚀 Setup on Other Devices

Follow these steps to set up the project on a new device.

### Prerequisites
- **Python 3.10+** (Recommended)
- **Ollama** installed and running ([install guide](https://ollama.ai))

### 1. Clone the Repository and Set Up Virtual Environment
```bash
# Navigate to the project folder
cd "oodp rag project."

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scriptsctivate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Pull Ollama Models
Ensure Ollama is running in the background, then pull the required models:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### 4. Build the Vector Store (Ingestion)
Before running the app, you need to embed the syllabus topics into ChromaDB:
```bash
python ingest.py --skip-scrape --reindex
```
*(This generates 229 LangChain Documents from the Syllabus KB, embeds them, and stores them in `vectorstore/`)*

### 5. Run the Application
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

### Optional Setup Commands
- **Incremental Ingestion:** `python ingest.py`
- **Rebuild With Scraping:** `python ingest.py --reindex`

---

## 🔑 Using an External Model API (e.g., Groq / OpenAI)

By default, this project uses **Ollama** to run Llama 3 locally. If you want to use an external API (like Groq, OpenAI, or Anthropic) to save local resources or get faster responses, follow these steps:

### 1. Install the Required LangChain Integration
Depending on your provider, install the required package:
```bash
# For Groq
pip install langchain-groq

# For OpenAI
pip install langchain-openai
```

### 2. Update `config.py`
Add your API key constant (or load it from `.env` using `python-dotenv`):
```python
import os

# Add your API Key (Make sure to avoid committing this!)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-groq-api-key-here")
# OR
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-openai-api-key-here")
```

### 3. Update `llm.py`
Change the `create_llm()` function to instantiate your new model instead of `OllamaLLM`.

**Example using Groq (Llama 3 70B):**
```python
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_TEMPERATURE

def create_llm():
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama3-70b-8192",
        temperature=LLM_TEMPERATURE
    )
```

**Example using OpenAI (GPT-4o):**
```python
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, LLM_TEMPERATURE

def create_llm():
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o",
        temperature=LLM_TEMPERATURE
    )
```
*Note: This only replaces the text generation model. The document embeddings will still use Ollama (`nomic-embed-text`). If you want to use external embeddings (like OpenAI embeddings), you must also update the `EMBEDDING_MODEL` logic in `ingest.py` and `retriever.py` to use `OpenAIEmbeddings`.*

---

## 🎯 Key Features

✅ **Syllabus-Aware**: Only answers academic questions from SRM curriculum  
✅ **Source Citations**: Shows which subjects/units were referenced with similarity scores  
✅ **Semantic Search**: Understands intent, not just keywords  
✅ **Query Rewriting**: Converts casual questions to academic queries  
✅ **Response Caching**: Fast repeated queries (24h TTL)  
✅ **Streaming**: Real-time token generation  
✅ **Metadata Filtering**: Filter by semester/subject  
✅ **Precision Filtering**: Removes irrelevant results (gap + subject isolation)  
✅ **Beautiful UI**: Modern glassmorphic design with animations  
✅ **Dark/Light Mode**: System-aware theming with manual toggle  
✅ **Conversational Memory**: Last 5 messages retained for context  
✅ **Refusal for Non-Academic**: Only refuses politics, entertainment, personal advice  

---

## 🧠 LLM System Prompt

The AI is instructed to:

1. **Act as a friendly senior student/young professor** - warm, clear, encouraging
2. **Start with simple definitions** - jargon-free explanations
3. **ALWAYS include practical examples:**
   - **Math subjects** → Solved numerical problems (step-by-step)
   - **Programming/CS** → Working code with comments
   - **Theory subjects** → Real-world analogies
   - **Science subjects** → Practical examples or solved problems
4. **Include ASCII mind-maps** for complex topics with multiple sub-concepts
5. **End with "Quick Revision"** - 3-5 bullet point takeaways
6. **Mention subject/semester/unit naturally** in the answer
7. **Never refuse academic questions** - always help
8. **Only refuse** politics, entertainment, personal advice, non-academic topics

---

## 📊 Coverage

### Semesters: 1-8

### Subject Count by Semester
- **Semester 1:** 8+ subjects (Calculus, Chemistry, C Programming, Economics, Cell Biology, etc.)
- **Semester 2:** 8+ subjects (Advanced Calculus, EEE, C++, Physics, EM Theory, etc.)
- **Semester 3:** 9+ subjects (DSA, COA, OS, Java, Digital Logic, Data Science, etc.)
- **Semester 4:** 6+ subjects (DAA, DBMS, AI, Probability, IoT, etc.)
- **Semester 5:** 5+ subjects (Discrete Math, Full Stack, FLA, CN, ML)
- **Semester 6:** 4+ subjects (Data Science, SEPM, Compiler Design)
- **Semester 7-8:** Behavioral Psychology + electives

### Total Coverage
- **40+ subjects**
- **200+ units**
- **Departments:** CSE, ECE, Mech, BioTech, Physics, Chemistry, Math

---

## 🔧 Maintenance

### Clear Response Cache
```bash
rm -rf .response_cache/*
```

### Reset Vector Store
```bash
rm -rf vectorstore/
python ingest.py --reindex
```

### Update Syllabus (Re-scrape)
```bash
python ingest.py --reindex
```

### Check Vector Store Size
```bash
python -c "import chromadb; c = chromadb.PersistentClient('vectorstore'); print(c.get_collection('srm_syllabus').count())"
```

### View Logs
Streamlit logs appear in terminal. Check for:
- Query rewriting output
- Active filters
- Response generation status

---

## 🧪 Testing

### Test Similarity Scoring
```bash
python test_similarity.py
```

### Test Ingestion
```bash
python ingest.py --skip-scrape
```

---

## 🐛 Known Limitations

1. **No images/attachments** in notes (Apple Notes limitation if using memo CLI)
2. **Ollama required** - must be running locally
3. **Scraping dependent** on thehelpers.vercel.app availability
4. **Single-user** - no authentication or multi-user support
5. **No web deployment** - runs locally only

---

## 🚀 Future Enhancements

- [ ] Add web deployment (Docker + cloud hosting)
- [ ] Multi-user support with authentication
- [ ] PDF export of conversations
- [ ] Voice input support
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard (popular questions, gaps in coverage)
- [ ] Auto-update syllabus on schedule
- [ ] Support for images/diagrams in responses

---

## 📝 Notes

- The syllabus KB (`generate_syllabus_kb.py`) is the **primary source** of truth
- PPT/PDF files in `data/` are **supplementary** content
- Precision filtering ensures only relevant subjects appear in citations
- Query rewriting resolves ambiguous pronouns using chat history
- Cache key includes chat history for context-aware caching

---

**Last Updated:** March 7, 2026  
**Version:** 1.0  
**Status:** Production Ready
