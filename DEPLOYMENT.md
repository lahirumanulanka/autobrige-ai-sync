# Deployment Guide

## Overview

This guide explains how to deploy and run the Strategy-Action Synchronization AI System in different environments.

## Prerequisites

### System Requirements

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended for model loading)
- 2GB disk space (for dependencies and model cache)
- Internet connection (initial setup to download sentence-transformers model)

### Software Requirements

- pip (Python package installer)
- git (for cloning repository)
- Virtual environment (venv, recommended)

## Installation Steps

### 1. Clone Repository

```bash
git clone <repository-url>
cd autobrige-ai-sync
```

### 2. Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate on Linux/Mac
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First-time installation will download the sentence-transformers model (~90MB) from HuggingFace. This requires internet access.

### 4. Configure Environment (Optional)

For LLM-powered recommendations:

```bash
# Copy example
cp .env.example .env

# Edit .env file and add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

**Without API key**: System runs in fallback mode with rule-based suggestions.

## Running the Application

### Streamlit Dashboard

```bash
streamlit run app/streamlit_app.py
```

The app will open at `http://localhost:8501`

### Command Line Interface (if implemented)

```bash
python -m src.cli --strategies data/strategic.json --actions data/action.json
```

## Testing

### Run Test Suite

```bash
# All tests
python tests/test_system.py

# Specific module tests
python -m pytest tests/ -v
```

### Manual Testing

1. **Without LLM (Fallback Mode)**:
   - Don't set OPENAI_API_KEY
   - Run Streamlit app
   - Verify rule-based suggestions are generated

2. **With LLM (RAG Mode)**:
   - Set OPENAI_API_KEY in .env
   - Run Streamlit app
   - Verify LLM-powered suggestions are generated

## Deployment Environments

### Local Development

Best for: Testing, development, presentations

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app/streamlit_app.py
```

### Docker Deployment

Best for: Production, cloud deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Download model during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t strategy-sync-ai .
docker run -p 8501:8501 -e OPENAI_API_KEY=sk-... strategy-sync-ai
```

### Cloud Deployment

#### Streamlit Cloud

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Deploy from repository
4. Add OPENAI_API_KEY in Secrets

#### Heroku

```bash
# Create Procfile
echo "web: streamlit run app/streamlit_app.py --server.port=\$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

#### AWS EC2

```bash
# Install on EC2 instance
sudo apt update
sudo apt install python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with screen/tmux
screen -S streamlit
streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
# Detach: Ctrl+A, D
```

## Offline Operation

### Pre-download Model

For environments without internet access:

```bash
# On machine with internet
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy cache to target machine
# Linux/Mac: ~/.cache/torch/sentence_transformers/
# Windows: C:\Users\<user>\.cache\torch\sentence_transformers\
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM generation (optional)

### Application Settings

Edit in `app/streamlit_app.py`:
- `top_k`: Default number of actions to retrieve (default: 5)
- `rec_threshold`: Recommendation threshold (default: 0.60)
- `persist_directory`: ChromaDB storage path (default: "chroma_db")

## Troubleshooting

### Model Download Fails

**Problem**: Cannot download sentence-transformers model

**Solutions**:
1. Check internet connection
2. Try manual download: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`
3. Use offline mode (see above)

### ChromaDB Lock Error

**Problem**: `sqlite3.OperationalError: database is locked`

**Solutions**:
1. Close other instances of the app
2. Delete `chroma_db/` folder and restart
3. Use different persist_directory

### OpenAI API Errors

**Problem**: API key invalid or rate limits

**Solutions**:
1. Verify API key is correct
2. Check OpenAI account has credits
3. System will fall back to rule-based mode

### Memory Issues

**Problem**: Out of memory during model loading

**Solutions**:
1. Use smaller embedding model
2. Increase system RAM
3. Use batch processing

## Performance Optimization

### Embedding Cache

The system caches embeddings in memory. For large datasets:
- Cache persists during session
- Clear cache: restart application
- Reduce memory: use smaller model

### Vector Database

ChromaDB is persistent:
- Index once, query multiple times
- Reset if data changes: `store.reset()`
- Backup: copy `chroma_db/` folder

## Security Considerations

1. **API Keys**: Never commit .env file to git
2. **Data Privacy**: Sensitive data sent to OpenAI (if using LLM)
3. **Access Control**: Deploy behind authentication if public
4. **HTTPS**: Use SSL/TLS in production

## Monitoring

### Logs

```bash
# Streamlit logs
streamlit run app/streamlit_app.py --logger.level=debug

# Application logs
tail -f logs/app.log
```

### Metrics to Track

- Response time
- Alignment score distribution
- LLM usage and costs
- Error rates

## Maintenance

### Regular Tasks

1. **Update Dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Backup Data**:
   ```bash
   cp -r chroma_db/ backups/chroma_db_$(date +%Y%m%d)
   ```

3. **Monitor Disk Space**:
   ```bash
   du -sh chroma_db outputs
   ```

## Support

For issues or questions:
1. Check README.md
2. Review logs
3. Open GitHub issue
4. Contact maintainer

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
