# SOP RAG MVP - Quick Start Guide

## Complete System Ready ✅

Backend + Frontend fully implemented and integrated.

## Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 16+
- ~8GB RAM for AI models

## 1. Start Backend Services (5 min)

```bash
cd /path/to/sop-rag-mvp
docker-compose up -d
```

Verify services:
```bash
curl http://localhost:5432  # PostgreSQL
curl http://localhost:6379  # Redis
```

## 2. Start FastAPI Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

Check: http://localhost:8000/docs

## 3. Start Celery Worker

```bash
cd backend
python celery_worker.py
```

## 4. Start React Frontend

```bash
cd frontend
npm install
npm run dev
```

Access: http://localhost:5173

## Usage (2 min)

1. **Upload Document**
   - Click "Documents" tab
   - Click "Upload Document"
   - Select a PDF file
   - Wait for processing (status → "completed")

2. **Ask Questions**
   - Click "Chat" tab
   - Click document to select it (blue highlight)
   - Type your question
   - Send and view response with citations

## API Status

```bash
# Health check
curl http://localhost:8000/health

# List documents
curl http://localhost:8000/api/v1/documents

# Submit query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is this about?"}'
```

## Run Tests

```bash
cd backend
pytest tests/test_integration.py -v
```

## Docker Compose Services

- **PostgreSQL** (5432) - Document/chunk storage
- **Redis** (6379) - Caching & Celery broker
- **MinIO** (9000) - Object storage
- **Ollama** (11434) - Local AI models
- **ChromaDB** (8001) - Vector database

## Troubleshooting

**Frontend can't connect to backend**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS in backend/app/main.py
# Should allow http://localhost:5173
```

**Documents won't upload**
```bash
# Check Celery worker is running
ps aux | grep celery

# Check PostgreSQL is running
docker-compose ps
```

**No search results**
```bash
# Check document processing is complete
curl http://localhost:8000/api/v1/documents

# Check ChromaDB has vectors
curl http://localhost:8001/api/v1/heartbeat
```

## Project Structure

```
sop-rag-mvp/
├── backend/              # FastAPI + Celery
│   ├── app/              # Application code
│   ├── tests/            # Integration tests (27 tests)
│   └── requirements.txt
├── frontend/             # React + TypeScript
│   ├── src/              # Components, stores, services
│   └── package.json
├── docker-compose.yml    # Services configuration
└── docs/                 # Architecture & guides
```

## Performance

- Document upload: < 1s
- Text extraction: 2-5s
- Embedding generation: 0.5-2s per chunk
- Query response: 2.5-6s end-to-end

## Next Steps

1. **Test** - Upload test PDFs and verify chat works
2. **Customize** - Modify frontend colors/branding
3. **Deploy** - Build and deploy to production
4. **Scale** - Add more Celery workers for parallel processing

## Support

- Backend API docs: http://localhost:8000/docs
- Frontend README: frontend/README.md
- Architecture: docs/ARCHITECTURE.md
- Integration guide: FRONTEND_INTEGRATION.md

---

**The complete RAG system is ready to use!**

For detailed documentation, see individual README files in each directory.
