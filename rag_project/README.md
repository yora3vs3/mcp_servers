# RAG Project Scaffolding

This directory contains modular scaffolding for a Retrieval-Augmented Generation (RAG) system. The pipeline is designed to be highly modular, separating document ingestion, text chunking, embedding generation, vector database indexing, document retrieval, and LLM orchestration.

---

## 📂 Architecture & Directory Layout

Each directory in `src/` represents a specific phase of the RAG pipeline:

```text
rag_project/
├── main.py            # Main entrypoint to run ingestion or querying pipelines
├── config.yaml        # Configuration parameters (database path, model models, parameters)
├── requirements.txt   # Pip package dependencies specific to the RAG modules
├── tests/             # Unit tests folder
│   └── test_app.py    # Test suite for components
└── src/               # Core implementation source code
    ├── ingestion/     # PDF, DOCX, TXT loaders & parsers
    ├── chunking/      # Character, recursive, or semantic text splitters
    ├── embeddings/    # HuggingFace, OpenAI, or local embedding model integrations
    ├── vectordb/      # Indexing and storing embeddings (Chroma, FAISS, Qdrant, etc.)
    ├── retrieval/     # Keyword (BM25), vector, or hybrid retrieval & re-ranking (Cross-Encoders)
    ├── prompts/       # System and user prompts for formatting context
    ├── llm/           # Local (Ollama, vLLM) or Cloud (Claude, OpenAI) API connectors
    ├── api/           # API handlers/routers (e.g. FastAPI) for serving the RAG app
    └── utils/         # Performance logging, file helpers, and general utilities
```

---

## 🛠️ Implementing the Pipeline

To implement the RAG pipeline, follow these suggested steps:

1. **Configure Settings**: Define your data directory, vector database choice, and embedding model parameters in [config.yaml](file:///d:/Prj1.0/rag_project/config.yaml).
2. **Ingestion & Chunking**: Write loaders in `ingestion/` to read documents and use `chunking/` to split texts into uniform pieces.
3. **Embeddings & VectorDB**: Generate embeddings in `embeddings/` and populate your vector store using modules in `vectordb/`.
4. **Retrieval**: Build hybrid searches (keyword + vector) in `retrieval/` and re-rank candidate documents.
5. **LLM Orchestration**: Format retrieved documents into system prompts under `prompts/` and run completions via `llm/`.
6. **Main Pipeline & API**: Orchestrate all steps in [main.py](file:///d:/Prj1.0/rag_project/main.py) and expose HTTP routes in `api/`.
