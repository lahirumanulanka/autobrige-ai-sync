# Quick Start Guide

## Prerequisites
- Python 3.10 or higher
- Internet connection (for first run to download ML model)
- pip package manager

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lahirumanulanka/autobrige-ai-sync.git
   cd autobrige-ai-sync
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: On first run, the system will download the sentence transformer model (~90MB) from HuggingFace. This requires an internet connection.

## Running the Application

### Option 1: Streamlit Dashboard (Recommended)

```bash
streamlit run app/streamlit_app.py
```

Then open your browser to `http://localhost:8501`

### Option 2: Run Tests

```bash
python tests/test_system.py
```

This will verify that all modules are working correctly.

### Option 3: Python Script

```python
from src.models import load_strategies, load_actions
from src.alignment import AlignmentEngine
from src.recommendations import generate_recommendations

# Load data
strategies = load_strategies('data/strategic.json')
actions = load_actions('data/action.json')

# Analyze alignment
engine = AlignmentEngine()
results = engine.analyze_alignment(strategies, actions, top_k=5)

# Generate recommendations
recommendations = generate_recommendations(results, strategies)

# Print results
print(f"Overall Score: {results['overall_synchronization_score']:.2f}%")
print(f"Coverage: {results['coverage_percentage']:.2f}%")
```

## Using the Dashboard

1. **Select Data Source:**
   - Use sample data (AutoBridge examples)
   - Or upload your own JSON files

2. **Run Analysis:**
   - Click "Run Synchronization Analysis"
   - Wait for processing (30-60 seconds)

3. **Review Results:**
   - View overall synchronization metrics
   - Explore strategy-wise alignment
   - Read recommendations

4. **Export:**
   - Save results to `outputs/` folder
   - Download as JSON

## Data Format

### Strategic Objectives JSON

```json
[
  {
    "id": "S1",
    "title": "Strategic Objective Title",
    "description": "Detailed description of the objective",
    "kpis": ["KPI 1", "KPI 2", "KPI 3"],
    "priority": "High"
  }
]
```

### Action Tasks JSON

```json
[
  {
    "id": "A1",
    "title": "Action Task Title",
    "description": "Detailed description of the action",
    "owner": "Team Name",
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "outputs": ["Output 1", "Output 2"]
  }
]
```

## Troubleshooting

### Model Download Issues

If you see errors about downloading from HuggingFace:
- Ensure you have internet connection
- Check firewall settings
- Try: `export HF_ENDPOINT=https://huggingface.co` (Linux/Mac)

### Import Errors

If you see `ModuleNotFoundError`:
- Make sure you're in the project root directory
- Verify virtual environment is activated
- Run: `pip install -r requirements.txt`

### ChromaDB Issues

If ChromaDB errors occur:
- Delete the `chroma_db/` folder
- Run the application again

## Next Steps

- Customize sample data with your organization's strategies and actions
- Adjust similarity thresholds in `src/alignment.py`
- Modify recommendation rules in `src/recommendations.py`
- Extend with additional analysis features

## Support

For issues or questions:
- Check the main README.md
- Review the code documentation
- Open an issue on GitHub
