# Strategy-Action Synchronization AI

## 🎓 MSc Coursework Project

**Project Name:** AutoBridge Strategy-Action Synchronization AI  
**Author:** MSc Student - AI & Machine Learning  
**Institution:** [Your University]  
**Academic Year:** 2024-2025

---

## 📋 Project Overview

This project implements an AI-powered system that analyzes and measures the **synchronization (alignment)** between a Strategic Plan and an Action Plan. The system uses state-of-the-art Natural Language Processing (NLP) techniques to semantically match strategic objectives with action tasks, providing quantitative alignment scores and intelligent recommendations for improvement.

The application is built specifically for **AutoBridge**, an import platform that helps importers streamline their operations. The system helps ensure that the company's strategic vision is properly reflected in day-to-day operational actions.

---

## 🎯 Problem Statement

Organizations often struggle with ensuring that their high-level strategic objectives are properly translated into concrete action plans. Key challenges include:

1. **Alignment Gap**: Strategic objectives may not have corresponding actions
2. **Resource Misallocation**: Actions may not support the most critical strategies
3. **Lack of Visibility**: Difficulty in measuring how well actions support strategies
4. **Manual Review**: Time-consuming manual review processes to assess alignment

This project addresses these challenges by:
- Automating alignment analysis using AI embeddings
- Providing quantitative synchronization scores (0-100%)
- Identifying weak alignment areas that need attention
- Generating actionable recommendations for improvement

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Streamlit UI   │ ◄─── User Interface & Visualization
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Alignment Engine Core               │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ Text Utils   │  │ Recommendation   │   │
│  │ Processing   │  │ System           │   │
│  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────┘
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ SentenceTransf. │   │   ChromaDB      │
│ (Embeddings)    │   │ Vector Store    │
└─────────────────┘   └─────────────────┘
         │                     │
         ▼                     ▼
    [Embeddings]         [Similarity Search]
```

### Component Breakdown

1. **Data Models (`src/models.py`)**
   - Pydantic models for type-safe data validation
   - `StrategicObjective`: id, title, description, KPIs, priority
   - `ActionTask`: id, title, description, owner, dates, outputs
   - Utility functions for loading JSON data

2. **Text Processing (`src/text_utils.py`)**
   - Text cleaning and normalization
   - Strategy-to-text conversion (title + description + KPIs)
   - Action-to-text conversion (title + description + outputs)
   - Deterministic and explainable transformations

3. **Vector Store (`src/vector_store.py`)**
   - ChromaDB integration with persistent storage
   - Action embedding storage and indexing
   - Cosine similarity-based retrieval
   - Query by embedding with top-K results

4. **Alignment Engine (`src/alignment.py`)**
   - Core synchronization logic
   - Sentence Transformer embeddings (all-MiniLM-L6-v2)
   - Strategy-to-action matching via vector similarity
   - Multi-level scoring system:
     - Per-action similarity scores
     - Per-strategy average (top 3 matches)
     - Overall synchronization score
     - Coverage percentage

5. **Recommendation System (`src/recommendations.py`)**
   - Rule-based intelligent recommendations
   - Context-aware suggestions based on:
     - Alignment level (Strong/Medium/Weak)
     - Strategy priority
     - KPI availability
     - Action coverage
   - Business-oriented language

6. **Streamlit Dashboard (`app/streamlit_app.py`)**
   - Interactive web interface
   - Data upload and sample data options
   - Real-time analysis and visualization
   - Downloadable JSON reports
   - Expandable detailed views

---

## 🤖 AI Techniques Used

### 1. **Sentence Embeddings**
- **Model**: `all-MiniLM-L6-v2` from Sentence Transformers
- **Purpose**: Convert text into dense 384-dimensional vectors
- **Why**: Captures semantic meaning, not just keyword matching
- **Benefit**: Similar meanings → similar vectors (e.g., "improve transparency" ≈ "enhance clarity")

### 2. **Vector Database (ChromaDB)**
- **Purpose**: Efficient similarity search over action embeddings
- **Method**: Cosine distance computation
- **Benefit**: Fast retrieval of top-K most relevant actions for each strategy
- **Persistent Storage**: Maintains vector index across sessions

### 3. **Cosine Similarity**
- **Formula**: `similarity = 1 - cosine_distance`
- **Range**: 0 (no similarity) to 1 (identical)
- **Purpose**: Measure semantic alignment between strategy and action embeddings
- **Interpretation**:
  - ≥0.6: Strong alignment
  - 0.4-0.6: Medium alignment
  - <0.4: Weak alignment

### 4. **Rule-Based Reasoning**
- **Purpose**: Generate contextual recommendations
- **Method**: Decision tree logic based on alignment scores, priority levels, and KPI presence
- **Benefit**: Explainable and auditable recommendations

---

## 📊 How Synchronization is Calculated

### Step-by-Step Process

1. **Text Representation**
   ```
   Strategy Text = "Title: [title] | Description: [desc] | KPIs: [kpis] | Priority: [priority]"
   Action Text = "Title: [title] | Description: [desc] | Outputs: [outputs] | Owner: [owner]"
   ```

2. **Embedding Generation**
   - Convert all strategies and actions to embeddings using Sentence Transformers
   - Each text → 384-dimensional vector

3. **Vector Indexing**
   - Store all action embeddings in ChromaDB
   - Build similarity search index

4. **Matching Process**
   - For each strategy:
     - Query ChromaDB with strategy embedding
     - Retrieve top-K most similar actions
     - Calculate cosine similarity scores

5. **Score Aggregation**
   - **Per-Strategy Score**: Average of top 3 matching actions
   - **Overall Score**: Average of all strategy scores × 100
   - **Coverage**: % of strategies with ≥2 "Strong" actions

6. **Classification**
   - Weak: score < 0.4
   - Medium: 0.4 ≤ score < 0.6
   - Strong: score ≥ 0.6

### Example Calculation

```
Strategy S1: "Enhance Import Cost Transparency"
Top 3 Actions:
  A1: "Develop Cost Calculator" → score = 0.75 (Strong)
  A2: "Create Cost Documentation" → score = 0.68 (Strong)
  A9: "Design Communication Templates" → score = 0.52 (Medium)

Strategy Score = (0.75 + 0.68 + 0.52) / 3 = 0.65 (Strong)
```

---

## 🚀 How to Run the Project

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lahirumanulanka/autobrige-ai-sync.git
   cd autobrige-ai-sync
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Streamlit dashboard**
   ```bash
   streamlit run app/streamlit_app.py
   ```

2. **Access the application**
   - Open your browser to `http://localhost:8501`

3. **Use the system**
   - Option 1: Use sample data (AutoBridge examples)
   - Option 2: Upload your own JSON files
   - Click "Run Synchronization Analysis"
   - Review results, recommendations, and download reports

### Sample Data

The project includes realistic sample data for AutoBridge:
- **Strategic Objectives** (`data/strategic.json`): 4 strategies
  - Enhance Import Cost Transparency
  - Strengthen Customer Trust
  - Streamline Importer Onboarding
  - Expand Auction Data Analytics
  
- **Action Tasks** (`data/action.json`): 10 actions
  - Cost calculator development
  - Documentation creation
  - Customer surveys
  - Onboarding workflows
  - Analytics dashboards
  - And more...

---

## 📁 Folder Structure

```
autobrige-ai-sync/
│
├── app/
│   └── streamlit_app.py        # Main Streamlit dashboard
│
├── src/
│   ├── models.py               # Pydantic data models
│   ├── text_utils.py           # Text processing utilities
│   ├── vector_store.py         # ChromaDB integration
│   ├── alignment.py            # Alignment engine core
│   └── recommendations.py      # Recommendation generator
│
├── data/
│   ├── strategic.json          # Sample strategic objectives
│   └── action.json             # Sample action tasks
│
├── outputs/                    # Saved analysis results
│
├── chroma_db/                  # ChromaDB persistent storage
│
├── tests/                      # Unit tests (optional)
│
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
└── LICENSE                     # License file
```

---

## 🔬 Key Features

### ✅ Automated Alignment Analysis
- No manual comparison needed
- Consistent, objective scoring
- Handles large strategy/action sets

### ✅ Semantic Understanding
- Goes beyond keyword matching
- Understands synonyms and context
- Captures intent and meaning

### ✅ Actionable Insights
- Clear alignment classifications
- Prioritized recommendations
- Specific improvement suggestions

### ✅ Interactive Dashboard
- User-friendly interface
- Real-time analysis
- Visual result presentation

### ✅ Export Capabilities
- JSON report downloads
- Timestamped output files
- Integration-ready format

---

## 📈 Future Improvements

### Technical Enhancements
1. **Advanced ML Models**
   - Fine-tune embeddings on domain-specific data
   - Experiment with larger models (e.g., `all-mpnet-base-v2`)
   - Multi-lingual support

2. **Enhanced Analytics**
   - Trend analysis over time
   - Comparative analysis across departments
   - Gap analysis visualization

3. **Automated Actions**
   - AI-generated action suggestions
   - Auto-draft action plans from strategies
   - Integration with project management tools

### Business Features
1. **Collaboration Tools**
   - Multi-user support
   - Comment and feedback system
   - Approval workflows

2. **Integration**
   - API for external systems
   - Database connectivity
   - Export to Excel/PDF

3. **Monitoring**
   - Periodic re-analysis
   - Alert system for declining alignment
   - Progress tracking dashboard

### Academic Extensions
1. **Evaluation Framework**
   - Expert validation study
   - Comparison with manual assessments
   - Statistical significance testing

2. **Alternative Approaches**
   - Graph-based alignment methods
   - LLM-based analysis (GPT-4)
   - Ensemble methods

---

## 📚 Technologies Used

- **Python 3.10+**: Core programming language
- **Streamlit**: Web dashboard framework
- **Sentence Transformers**: Embedding generation
- **ChromaDB**: Vector database
- **Pydantic**: Data validation
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation
- **scikit-learn**: ML utilities

---

## 📝 MSc Submission Notes

### What to Include in Your Report

1. **Screenshots**
   - Dashboard home page
   - Overall synchronization metrics
   - Strategy-wise alignment table
   - Detailed strategy analysis
   - Recommendations section
   - JSON download example

2. **Results**
   - Analysis output from sample data
   - Comparison with manual assessment
   - Processing time metrics

3. **Code Highlights**
   - Embedding generation logic
   - Similarity calculation
   - Recommendation rules

4. **Discussion Points**
   - Why semantic embeddings work better than TF-IDF
   - Trade-offs in model selection
   - Limitations and assumptions
   - Ethical considerations

### Suggested Evaluation Metrics

- **Accuracy**: Compare with manual expert alignment scores
- **Precision/Recall**: For weak alignment detection
- **Execution Time**: Scalability analysis
- **User Feedback**: Usefulness of recommendations

---

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

---

## 👤 Author

**[Your Name]**  
MSc Student - Artificial Intelligence & Machine Learning  
[Your University]  
[Your Email]

---

## 🙏 Acknowledgments

- AutoBridge platform for the use case inspiration
- Sentence Transformers library developers
- ChromaDB team for the vector database
- Streamlit for the excellent UI framework

---

## 📞 Contact

For questions, feedback, or collaboration:
- Email: [your-email@university.edu]
- GitHub: [your-github-profile]
- LinkedIn: [your-linkedin-profile]

---

*This project demonstrates the application of modern NLP and AI techniques to solve real-world business problems in strategic planning and execution alignment.*
