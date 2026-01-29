# Strategy-Action Synchronization AI System

**MSc Coursework Project** - RAG-based system for aligning strategic objectives with action tasks

## Problem Statement

Organizations often struggle to ensure that their operational actions align with strategic objectives. This misalignment leads to:
- Wasted resources on low-impact activities
- Strategic goals that remain unachieved
- Lack of visibility into alignment gaps
- Difficulty prioritizing actions

This system addresses these challenges by:
1. **Quantifying alignment** between strategies and actions using semantic similarity
2. **Identifying gaps** where strategies lack supporting actions
3. **Generating recommendations** using RAG (Retrieval-Augmented Generation)
4. **Providing actionable insights** for improving synchronization

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                              │
│  Strategic Objectives (JSON) + Action Tasks (JSON)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                 TEXT PROCESSING                             │
│  • Clean and normalize text                                 │
│  • Convert objects to deterministic strings                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              EMBEDDING GENERATION                           │
│  SentenceTransformers (all-MiniLM-L6-v2)                    │
│  • 384-dimensional vectors                                  │
│  • Normalized L2 distance                                   │
│  • In-memory caching                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              VECTOR DATABASE                                │
│  ChromaDB (Persistent)                                      │
│  • Cosine similarity space                                  │
│  • Actions indexed with metadata                            │
│  • Fast approximate nearest neighbor search                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            CONTEXT RETRIEVAL                                │
│  Top-K Similar Actions per Strategy                         │
│  • Query strategy embedding                                 │
│  • Retrieve K most similar actions                          │
│  • Label strength: Strong/Medium/Weak                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          ALIGNMENT SCORING                                  │
│  • Compute avg_top3_similarity per strategy                 │
│  • Overall synchronization score                            │
│  • Coverage percentage (strategies with ≥2 strong matches)  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         PROMPT AUGMENTATION (RAG)                           │
│  Build Context:                                             │
│  • Strategy details (title, description, KPIs)              │
│  • Retrieved actions with similarity scores                 │
│  • Current alignment metrics                                │
│  • Clear separation: CONTEXT vs TASK                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            LLM GENERATION                                   │
│  IF OPENAI_API_KEY exists:                                  │
│    • Call GPT-3.5-turbo with augmented prompt               │
│    • Generate structured suggestions                        │
│  ELSE (Fallback Mode):                                      │
│    • Rule-based suggestion generation                       │
│    • Deterministic output based on alignment score          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              OUTPUT LAYER                                   │
│  • Improvement suggestions (actionable)                     │
│  • New action proposals (title, description, owner)         │
│  • KPI recommendations                                      │
│  • Risk assessment                                          │
│  • JSON exports (alignment_results, recommendations)        │
└─────────────────────────────────────────────────────────────┘
```

## Technical Components

### 1. Embeddings (Semantic Understanding)

**Purpose**: Convert text to numerical vectors that capture semantic meaning

**Implementation**:
- Model: `all-MiniLM-L6-v2` (384 dimensions)
- Framework: SentenceTransformers
- Features:
  - L2 normalization for cosine similarity
  - In-memory caching for efficiency
  - Batch processing support

**Why it matters**: Embeddings allow us to measure semantic similarity between strategies and actions, even when they use different words but express similar concepts.

### 2. Vector Database (Efficient Retrieval)

**Purpose**: Store and query embeddings efficiently

**Implementation**:
- Database: ChromaDB (persistent)
- Distance metric: Cosine similarity
- Features:
  - HNSW (Hierarchical Navigable Small World) index
  - Metadata storage
  - Fast approximate nearest neighbor search

**Why it matters**: Vector databases enable sub-second retrieval of relevant actions from thousands of candidates, making the system scalable.

### 3. Retrieval (Context Selection)

**Purpose**: Find the most relevant actions for each strategy

**Implementation**:
- Top-K retrieval (configurable K)
- Similarity scoring (0-1 scale)
- Strength labeling:
  - Strong: ≥0.75
  - Medium: 0.55-0.75
  - Weak: <0.55

**Why it matters**: Retrieval provides grounded context for the LLM, reducing hallucination and ensuring recommendations are based on actual available actions.

### 4. RAG (Grounded Generation)

**Purpose**: Generate recommendations based on retrieved context

**Implementation**:
- Prompt structure:
  ```
  SYSTEM: Expert consultant instructions
  USER: CONTEXT (strategy + retrieved actions)
        TASK (what to generate)
  ```
- Safeguards:
  - Explicit instruction to use only provided context
  - Clear separation of data and task
  - Structured output format

**Why it matters**: RAG combines the semantic understanding of LLMs with factual grounding from retrieval, producing accurate and relevant recommendations.

## Installation & Setup

### 1. Prerequisites

- Python 3.10 or higher
- pip package manager
- (Optional) OpenAI API key for LLM generation

### 2. Clone Repository

```bash
git clone <repository-url>
cd autobrige-ai-sync
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment (Optional)

To enable LLM-powered suggestions:

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

**Note**: The system works without an API key using rule-based fallback suggestions.

## Usage

### Running the Streamlit Dashboard

```bash
streamlit run app/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the UI

1. **Choose Data Source**:
   - Sample Data: Use provided AutoBridge examples
   - Upload Files: Provide your own JSON files

2. **Configure Parameters**:
   - Top-K: Number of actions to retrieve per strategy (3-10)
   - Recommendation Threshold: Similarity below which to generate detailed suggestions

3. **Enable RAG** (if API key available):
   - Check "Enable RAG" to use LLM generation
   - Uncheck for rule-based fallback mode

4. **Run Synchronization**:
   - Click the "Run Synchronization" button
   - Wait for analysis to complete

5. **Review Results**:
   - Overall metrics (score, coverage)
   - Strategy-action mapping table
   - Detailed analysis per strategy
   - Recommendations and suggestions

6. **Download Outputs**:
   - `alignment_results.json`: Full alignment analysis
   - `recommendations.json`: Generated recommendations
   - `eval_summary.csv`: Evaluation metrics table

## Data Format

### Strategic Objectives JSON

```json
[
  {
    "id": "S001",
    "title": "Strategic Objective Title",
    "description": "Detailed description of the strategic goal",
    "kpis": [
      "KPI 1",
      "KPI 2"
    ],
    "priority": "High"
  }
]
```

### Action Tasks JSON

```json
[
  {
    "id": "A001",
    "title": "Action Task Title",
    "description": "Detailed description of the action",
    "owner": "Team Name",
    "start_date": "2024-01-15",
    "end_date": "2024-03-30",
    "outputs": [
      "Deliverable 1",
      "Deliverable 2"
    ]
  }
]
```

## Outputs

### 1. alignment_results.json

Contains:
- Overall synchronization score (0-100)
- Coverage percentage
- Per-strategy mapping with top-K actions
- Weak strategies list

### 2. recommendations.json

Contains:
- Per-strategy recommendations
- Improvement suggestions
- New action proposals
- KPI recommendations
- Risk assessment

### 3. eval_summary.csv

Contains:
- Strategy ID and title
- Alignment scores
- Top matching action
- Strength labels
- Summary statistics

## Evaluation Methodology

### Coverage Metrics

- **Overall Score**: Average of all strategy avg_top3_similarity scores (×100)
- **Coverage %**: Percentage of strategies with ≥2 strong matches (similarity ≥0.75)
- **Distribution**: Mean, median, min, max, std dev of similarity scores

### Precision@K

For each strategy, we measure:
- Top-1 precision: Is the top action truly relevant?
- Top-3 average: Quality of the 3 most similar actions
- Strong match count: How many actions have similarity ≥0.75?

### Usefulness Rating

Qualitative assessment of recommendations:
- Specificity: Are suggestions concrete and actionable?
- Relevance: Do they address actual alignment gaps?
- Feasibility: Can they be realistically implemented?

### Evaluation Ideas for Report

1. **Baseline Comparison**:
   - Random selection
   - Keyword matching only
   - TF-IDF similarity

2. **Human Evaluation**:
   - Expert review of top-K retrieved actions
   - Rating of recommendation quality
   - Comparison with manual analysis

3. **Ablation Studies**:
   - Impact of different embedding models
   - Effect of top-K value
   - RAG vs fallback mode comparison

4. **Metrics to Track**:
   - Retrieval accuracy (how many top-K are truly relevant?)
   - Recommendation acceptance rate (if deployed)
   - Time savings vs manual analysis
   - User satisfaction scores

## Project Structure

```
autobrige-ai-sync/
├── app/
│   ├── __init__.py
│   └── streamlit_app.py          # Streamlit UI
├── src/
│   ├── __init__.py
│   ├── models.py                 # Pydantic data models
│   ├── text_utils.py             # Text processing utilities
│   ├── embeddings.py             # SentenceTransformer wrapper
│   ├── vector_store.py           # ChromaDB wrapper
│   ├── retrieval.py              # Top-K retrieval logic
│   ├── alignment.py              # Alignment engine
│   ├── rag_prompt.py             # Prompt builder
│   ├── llm_client.py             # OpenAI client
│   ├── rag_engine.py             # RAG pipeline
│   ├── recommendations.py        # Recommendation generator
│   └── evaluation.py             # Evaluation metrics
├── data/
│   ├── strategic.json            # Sample strategies
│   └── action.json               # Sample actions
├── outputs/                      # Generated outputs (JSON, CSV)
├── chroma_db/                    # ChromaDB persistence
├── tests/                        # Test suite
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Key Features

### 1. Modular Design

Each component is self-contained with clear interfaces:
- Easy to test individual modules
- Can swap implementations (e.g., different embedding models)
- Clean separation of concerns

### 2. Explainability

The system provides transparency:
- Shows similarity scores for each match
- Displays retrieved context used for generation
- Labels strength of each connection
- Exports detailed JSON for audit

### 3. Fallback Mode

Works without LLM API key:
- Rule-based suggestion generation
- Deterministic outputs
- Based on alignment score thresholds
- Maintains same output structure

### 4. Scalability

Designed for growth:
- Vector database handles thousands of actions
- Batch embedding generation
- Persistent storage (no re-indexing)
- Efficient caching

## Technologies

- **Python 3.10+**: Core language
- **Streamlit**: Interactive web UI
- **SentenceTransformers**: Embedding generation
- **ChromaDB**: Vector database
- **Pydantic**: Data validation
- **OpenAI API**: LLM generation (optional)
- **Pandas**: Data analysis
- **NumPy**: Numerical operations

## Future Enhancements

1. **Advanced Evaluation**:
   - Automated A/B testing of recommendations
   - User feedback loop integration
   - Precision@K validation

2. **Enhanced RAG**:
   - Better LLM response parsing (JSON mode)
   - Multi-turn conversation for refinement
   - Custom fine-tuned models

3. **Additional Features**:
   - Time-series analysis of alignment trends
   - What-if scenario modeling
   - Automated action prioritization
   - Integration with project management tools

4. **Performance**:
   - Asynchronous processing
   - Distributed embedding generation
   - Incremental index updates

## License

See LICENSE file for details.

## Contact

For questions or support, please open an issue on the repository.

---

**MSc Coursework Project** - Demonstrating application of RAG, vector databases, and semantic search for strategic alignment.
