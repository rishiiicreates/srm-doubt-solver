# 🎓 SRM College Doubt-Solving Agent

An AI-powered academic assistant that answers student doubts for **all SRM Institute of Science and Technology syllabus topics** — covering **56 subjects across 7 semesters**.

Built with **Ollama (Llama 3)**, **ChromaDB**, **LangChain**, and **Streamlit**.

---

## ✨ Features

- **Full Syllabus Coverage** — 56 subjects, 229 topic units, semesters 1-7
- **Intelligent Doubt Solving** — Detailed, professor-quality explanations
- **Subject & Semester Filtering** — Filter answers by specific semester or subject
- **Source Citations** — Every answer cites the relevant Subject, Semester, and Unit
- **Off-Topic Refusal** — Politely declines non-academic questions
- **Query Rewriting** — Rewrites casual student queries for better retrieval
- **Response Caching** — Caches answers for instant repeat lookups
- **Streaming Responses** — Real-time token streaming in the chat UI
- **Beautiful UI** — Dark glassmorphic design with gradient accents

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  Streamlit   │────▶│  LLM Chain   │────▶│  Ollama   │
│  Chat UI     │     │  (llm.py)    │     │  Llama 3  │
└──────┬───────┘     └──────┬───────┘     └───────────┘
       │                    │
       │              ┌─────▼──────┐     ┌────────────┐
       │              │  Retriever  │────▶│  ChromaDB  │
       │              │(retriever.py│     │ VectorStore│
       │              └────────────┘     └────────────┘
       │                                       ▲
       │              ┌────────────┐           │
       └─────────────▶│   Ingest   │───────────┘
                      │ (ingest.py)│
                      └─────┬──────┘
                            │
                      ┌─────▼──────┐
                      │Syllabus KB │
                      │ 229 topics │
                      └────────────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit chat UI with sidebar filters |
| `config.py` | All configuration constants and system prompt |
| `llm.py` | LLM chain, query rewriting, caching, streaming |
| `retriever.py` | ChromaDB similarity search with metadata filtering |
| `ingest.py` | Ingestion pipeline — embeds and stores in ChromaDB |
| `generate_syllabus_kb.py` | Comprehensive syllabus knowledge base (56 subjects) |
| `utils/chunker.py` | Token-aware sliding window chunker |
| `utils/downloader.py` | Web scraper for thehelpers.vercel.app (optional) |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** installed and running ([install guide](https://ollama.ai))

### 1. Clone and setup

```bash
cd "oodp rag project."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Pull Ollama models

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### 3. Run ingestion

```bash
python3 ingest.py --skip-scrape --reindex
```

This will:
- Generate 229 syllabus KB documents covering all subjects
- Embed them using `nomic-embed-text`
- Store in ChromaDB vector store

### 4. Launch the app

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📚 Subjects Covered

### Semester 1 (13 subjects)
Calculus & Linear Algebra, Chemistry, Philosophy of Engineering, Computational Biology, Programming for Problem Solving (C), Economics, Biomedical Sensors, Foreign Languages, Cell Biology, Microbiology, Physical & Analytical Chemistry, Biochemistry, Civil & Mechanical Workshop

### Semester 2 (9 subjects)
Advanced Calculus & Complex Analysis, Electrical & Electronics Engineering, Semiconductor Physics, Physics-Mechanics, Object Oriented Design & Programming (C++), Communicative English, Electromagnetic Physics, Engineering Mechanics, Electronic System & PCB Design

### Semester 3 (15 subjects)
Data Structures & Algorithm, Computer Organization & Architecture, Operating Systems, Transforms & Boundary Value Problems, Advanced Programming Practice (Java), Design Thinking, Digital Logic Design, Solid State Devices, Electromagnetic Theory, Basic Chemical Engineering, Genetics & Cytogenetics, Social Engineering, Numerical Methods, Foundation of Data Science, Bioprocess Principles

### Semester 4 (10 subjects)
Design & Analysis of Algorithms, Database Management Systems, Artificial Intelligence, Probability & Queueing Theory, Social Engineering, Cell Communication & Signaling, Software Process, Chemical Engineering Principles, Molecular Biology, Internet of Things (IoT)

### Semester 5 (5 subjects)
Discrete Mathematics, Full Stack Web Development, Formal Language & Automata, Computer Networks, Machine Learning

### Semester 6 (3 subjects)
Data Science, Software Engineering & Project Management, Compiler Design

### Semester 7 (1 subject)
Behavioral Psychology

---

## 🔧 Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_MODEL` | `llama3` | Ollama model for generation |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Ollama model for embeddings |
| `LLM_NUM_CTX` | `4096` | Context window size |
| `TOP_K` | `8` | Number of chunks to retrieve |
| `SIMILARITY_THRESHOLD` | `0.3` | Minimum similarity score |
| `CHUNK_SIZE` | `200` | Target tokens per chunk |

---

## 🧪 Example Queries

- "Explain Dijkstra's shortest path algorithm"
- "What is the difference between TCP and UDP?"
- "Explain inheritance types in C++ OOP"
- "What is normalization in DBMS? Explain all normal forms"
- "Explain the working of an AVL tree with rotations"
- "What is Fourier Transform and its applications?"
- "Explain the OSI model layers"

Off-topic queries like "Who is the Prime Minister?" will be politely refused.

---

## 📁 Project Structure

```
oodp rag project./
├── app.py                    # Streamlit chat UI
├── config.py                 # Configuration constants
├── llm.py                    # LLM chain & streaming
├── retriever.py              # ChromaDB retrieval
├── ingest.py                 # Ingestion pipeline
├── generate_syllabus_kb.py   # Syllabus knowledge base
├── requirements.txt          # Python dependencies
├── utils/
│   ├── chunker.py            # Token-aware chunker
│   └── downloader.py         # Web scraper (optional)
├── data/                     # Supplementary PPT files (optional)
├── vectorstore/              # ChromaDB persistence
└── venv/                     # Python virtual environment
```

---

## 🛠️ How It Works

1. **Syllabus KB** — `generate_syllabus_kb.py` contains detailed topic descriptions for every subject/unit in the SRM curriculum
2. **Ingestion** — `ingest.py` generates 229 LangChain Documents from the KB, embeds them with `nomic-embed-text`, and stores in ChromaDB
3. **Retrieval** — When a student asks a question, `retriever.py` finds the most relevant syllabus topics using cosine similarity
4. **Generation** — `llm.py` sends the matched topics as context to Llama 3, which generates a detailed, comprehensive answer
5. **Guardrails** — If no syllabus topic matches (similarity < threshold), the system refuses the question

The key insight: the syllabus KB tells the LLM **what topics are valid**, and the LLM answers from its comprehensive training knowledge. This gives detailed, accurate answers without needing to download hundreds of PPT files.

---

## 📝 License

This project is for educational purposes at SRM Institute of Science and Technology.
