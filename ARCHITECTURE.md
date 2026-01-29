# System Architecture Visualization

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                    (Streamlit Dashboard)                            │
│  • Upload/Select Data                                               │
│  • Configure Parameters (top-k, threshold, RAG on/off)             │
│  • View Results & Download Outputs                                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA INGESTION                                 │
│  src/models.py: Load & Validate with Pydantic                       │
│  • Strategic Objectives (JSON) → StrategicObjective[]               │
│  • Action Tasks (JSON) → ActionTask[]                               │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TEXT PROCESSING                                  │
│  src/text_utils.py: Convert to Embeddings-Ready Text               │
│  • strategy_to_text(): "Title: X | Description: Y | KPIs: Z"        │
│  • action_to_text(): "Title: A | Description: B | Owner: C"         │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  EMBEDDING GENERATION                               │
│  src/embeddings.py: SentenceTransformer Wrapper                     │
│  • Model: all-MiniLM-L6-v2 (384 dimensions)                         │
│  • In-memory caching for efficiency                                 │
│  • L2 normalization for cosine similarity                           │
│  Input: Text strings → Output: numpy float32 vectors                │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   VECTOR INDEXING                                   │
│  src/vector_store.py: ChromaDB Persistent Storage                   │
│  • Collection: "actions" with cosine similarity                     │
│  • Metadata: action_id, title, owner, dates                         │
│  • Persistent at: chroma_db/                                        │
│  Indexed: All action embeddings with metadata                       │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  SIMILARITY SEARCH                                  │
│  src/retrieval.py: Top-K Retrieval                                  │
│  For each strategy:                                                 │
│  • Query with strategy embedding                                    │
│  • Retrieve K most similar actions                                  │
│  • Label strength (Strong ≥0.75, Medium ≥0.55, Weak <0.55)         │
│  Output: List of {action, similarity, strength}                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ALIGNMENT SCORING                                 │
│  src/alignment.py: AlignmentEngine                                  │
│  Compute metrics:                                                   │
│  • avg_top3_similarity per strategy                                 │
│  • Overall score = mean(all avg_top3) × 100                         │
│  • Coverage = % strategies with ≥2 strong matches                   │
│  • Identify weak strategies (score < 0.55)                          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
         ┌──────────────┐   ┌──────────────┐
         │ If avg < 0.60│   │ If avg ≥ 0.60│
         │  (Weak)      │   │  (Good)      │
         └──────┬───────┘   └──────┬───────┘
                │                   │
                ▼                   ▼
┌───────────────────────┐   ┌──────────────────┐
│ DETAILED RAG PIPELINE │   │ LIGHT SUGGESTIONS│
│ src/rag_engine.py     │   │ src/recommend.py │
└───────┬───────────────┘   └──────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   PROMPT AUGMENTATION                               │
│  src/rag_prompt.py: Build Context + Task                            │
│  CONTEXT BLOCK:                                                     │
│  • Strategy: id, title, description, KPIs, priority                 │
│  • Current alignment score & status                                 │
│  • Retrieved actions: id, title, similarity, owner, dates           │
│  TASK:                                                              │
│  • Generate improvement suggestions                                 │
│  • Propose new actions                                              │
│  • Recommend KPIs                                                   │
│  • Assess risks                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
         ┌──────────────┐   ┌──────────────┐
         │ If LLM Key   │   │ No LLM Key   │
         │ Available    │   │ (Fallback)   │
         └──────┬───────┘   └──────┬───────┘
                │                   │
                ▼                   ▼
┌───────────────────────┐   ┌──────────────────┐
│ LLM GENERATION        │   │ RULE-BASED       │
│ src/llm_client.py     │   │ SUGGESTIONS      │
│                       │   │ src/rag_engine.py│
│ • OpenAI GPT-3.5      │   │                  │
│ • System + User prompt│   │ • Deterministic  │
│ • Timeout: 30s        │   │ • Score-based    │
│ • Parse response      │   │ • Same structure │
└───────┬───────────────┘   └──────┬───────────┘
        │                           │
        └──────────┬────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STRUCTURED OUTPUT                                  │
│  src/recommendations.py: Format Results                             │
│  For each strategy:                                                 │
│  • strategy_id, strategy_title                                      │
│  • avg_similarity, retrieved_actions[]                              │
│  • suggestions[] (actionable improvements)                          │
│  • new_actions[] (proposals with details)                           │
│  • kpis[] (measurement recommendations)                             │
│  • risks[] (potential challenges)                                   │
│  • llm_enabled (true/false)                                         │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EVALUATION & EXPORT                              │
│  src/evaluation.py: Compute Metrics & Export                        │
│  • Coverage metrics (strong/medium/weak counts)                     │
│  • Distribution statistics (mean, median, std)                      │
│  • CSV summary table                                                │
│  Outputs:                                                           │
│  • outputs/alignment_results.json                                   │
│  • outputs/recommendations.json                                     │
│  • outputs/eval_summary.csv                                         │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     VISUALIZATION                                   │
│  Streamlit UI: Display & Download                                   │
│  • Overall metrics dashboard                                        │
│  • Strategy mapping table                                           │
│  • Detailed per-strategy analysis                                   │
│  • Recommendations display                                          │
│  • Download buttons for JSON/CSV                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Dependency Graph

```
streamlit_app.py
    ├── models.py
    │   └── (Pydantic, json)
    │
    ├── alignment.py
    │   ├── models.py
    │   ├── text_utils.py
    │   ├── embeddings.py
    │   │   └── (sentence-transformers)
    │   ├── vector_store.py
    │   │   └── (chromadb)
    │   └── retrieval.py
    │
    ├── recommendations.py
    │   ├── models.py
    │   └── rag_engine.py
    │       ├── rag_prompt.py
    │       ├── llm_client.py
    │       │   └── (openai, dotenv)
    │       └── models.py
    │
    └── evaluation.py
        └── (pandas, numpy)
```

## Data Flow

```
Strategy JSON ──┐
                ├──> Load & Validate ──> Text Conversion ──> Embeddings ──┐
Action JSON ────┘                                                          │
                                                                           │
                                    ┌──────────────────────────────────────┘
                                    │
                                    ▼
                              Vector Database
                              (ChromaDB Index)
                                    │
                                    ▼
                          Similarity Search (Top-K)
                                    │
                                    ▼
                            Alignment Scoring
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
            Weak Alignment                  Strong Alignment
          (score < threshold)               (score ≥ threshold)
                    │                               │
                    ▼                               ▼
              RAG Pipeline                    Light Suggestions
         (Context + LLM/Fallback)                   │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                            Recommendations
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
            JSON Outputs                      CSV Reports
         (alignment, recommendations)      (eval_summary)
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│          PRESENTATION LAYER             │
│  • Streamlit (Interactive UI)           │
│  • HTML/CSS (Auto-generated)            │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
│  • Python 3.10+                         │
│  • Pydantic (Data validation)           │
│  • NumPy (Numerical operations)         │
│  • Pandas (Data analysis)               │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            AI/ML LAYER                  │
│  • SentenceTransformers (Embeddings)    │
│  • OpenAI API (LLM generation)          │
│  • scikit-learn (Utilities)             │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          DATA LAYER                     │
│  • ChromaDB (Vector database)           │
│  • JSON (Configuration & I/O)           │
│  • CSV (Reports)                        │
└─────────────────────────────────────────┘
```

## Key Design Patterns

1. **Repository Pattern**: `vector_store.py` abstracts ChromaDB operations
2. **Factory Pattern**: `EmbeddingModel` creates and caches embeddings
3. **Strategy Pattern**: RAG vs Fallback mode selection
4. **Pipeline Pattern**: Sequential processing through modules
5. **Observer Pattern**: Streamlit reactive UI updates

## Scalability Considerations

```
Current Scale:
• Strategies: ~10-100
• Actions: ~50-1000
• Response Time: <30s

Optimization Paths:
• Batch Processing: Process strategies in parallel
• Caching: Redis for embedding cache
• Async: Async I/O for LLM calls
• Distributed: Multiple ChromaDB instances

Future Scale:
• Strategies: 1000+
• Actions: 10,000+
• Response Time: <60s
```
