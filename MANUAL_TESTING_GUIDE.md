# Manual End-to-End Testing Guide

This guide walks you through testing the complete SOP RAG MVP system manually.

## Prerequisites

- Docker & Docker Compose installed
- Python 3.10+ with virtual environment
- Node.js 16+ with npm
- 8GB+ RAM for running services and models
- Terminal/Shell access

## System Overview

The system consists of 5 major components:
1. **PostgreSQL** - Document/chunk storage
2. **Redis** - Caching and Celery broker
3. **FastAPI Backend** - REST API and WebSocket server
4. **Celery Worker** - Async document processing
5. **React Frontend** - Web UI for interaction

## Step 1: Start Docker Services (5 min)

Open Terminal 1:

```bash
cd /home/dabhi/projects/sop-rag-mvp
docker-compose up -d postgres redis
```

Verify services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME               STATUS
sop-rag-postgres   Up (health: healthy)
sop-rag-redis      Up (health: healthy)
```

Check PostgreSQL connection:
```bash
docker exec sop-rag-postgres psql -U user -d sop_rag -c "SELECT version();"
```

## Step 2: Start FastAPI Backend (5 min)

Open Terminal 2:

```bash
cd /home/dabhi/projects/sop-rag-mvp/backend

# Activate virtual environment
source venv/bin/activate

# Start backend
python -m app.main
```

You should see output like:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
2025-10-22 07:XX:XX.XXX | INFO | app.database:init_db:47 - Database initialized
INFO:     Application startup complete [uvicorn]
```

Open another tab/window to verify:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected",
    ...
  }
}
```

## Step 3: Start Celery Worker (3 min)

Open Terminal 3:

```bash
cd /home/dabhi/projects/sop-rag-mvp/backend

# Activate same virtual environment
source venv/bin/activate

# Start worker
python celery_worker.py
```

You should see:
```
 ---------- celery@hostname v5.3.x
 |--- celery [queue.control]
[2025-10-22 XX:XX:XX,XXX: WARNING/MainProcess]
 celery@hostname ready.
```

## Step 4: Start React Frontend (5 min)

Open Terminal 4:

```bash
cd /home/dabhi/projects/sop-rag-mvp/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Expected output:
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

## Step 5: Access and Test the System

### Open Web Browser

Navigate to: http://localhost:5173

You should see the SOP RAG MVP interface with two tabs:
- 💬 Chat
- 📄 Documents

### Test Documents Tab

1. Click **"Upload Document"** button
2. Select a PDF file from your computer
3. You'll see the upload progress
4. Document should appear in the list with status "pending" → "processing" → "completed"
5. Wait for processing to complete (typically 5-10 seconds)
6. Verify chunk counts show text/image/table statistics

### Test Chat Tab

1. Go to **"Chat"** tab
2. Click on a processed document to select it (should show blue highlight)
3. Type a question about the document
   - For example: "What is the main topic of this document?"
   - Or: "Summarize the key points"
4. Press Enter or click Send
5. Wait for response (typically 2-6 seconds)
6. Response should appear with citations showing source documents

### Test Real-time Updates

1. Upload another document while chat is open
2. In Chat tab, watch the WebSocket connection indicator
3. You should see processing progress updates in real-time

## API Testing (Command Line)

### Health Check

```bash
curl http://localhost:8000/health | jq '.'
```

### List Documents

```bash
curl http://localhost:8000/api/v1/documents | jq '.documents'
```

### Submit Query

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What is this document about?",
    "document_ids": ["<document-id-here>"]
  }' | jq '.'
```

### WebSocket Connection

Test WebSocket manually:

```bash
# Using wscat (npm install -g wscat)
wscat -c ws://localhost:8000/ws
# Then send: {"action": "ping"}
```

## Troubleshooting

### Backend won't start

**Error**: Database connection failed

**Solution**:
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check credentials match docker-compose.yml
# Default: user:password
grep "POSTGRES_" docker-compose.yml
```

**Error**: Redis connection failed

**Solution**:
```bash
# Verify Redis is running
docker-compose ps redis

# Check Redis connectivity
redis-cli ping
```

### Frontend can't connect to backend

**Error**: Connection refused on localhost:8000

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/`
2. Check frontend API config in `frontend/src/services/api.ts`
3. Verify port 8000 isn't blocked by firewall

### Document upload fails

**Error**: Upload button does nothing

**Solution**:
1. Check backend logs for errors
2. Verify Celery worker is running: `ps aux | grep celery`
3. Check Redis is accepting connections

### Chat query returns error

**Error**: "Sorry, there was an error processing your query"

**Solution**:
1. Verify at least one document is processed
2. Check vector store has chunks indexed
3. Look at backend logs for detailed error message
4. Verify Ollama is accessible (if using local LLM)

## Performance Expectations

### Document Processing
- Small PDF (< 5MB): 5-10 seconds
- Medium PDF (5-20MB): 10-30 seconds
- Large PDF (> 20MB): 30-60+ seconds

### Query Response
- Retrieval: 50-200ms
- Reranking: 100-500ms
- LLM Generation: 2-5 seconds
- **Total**: 2.5-6 seconds end-to-end

### System Requirements
- Minimum: 4GB RAM, 2GB disk
- Recommended: 8GB+ RAM, 10GB+ disk
- For GPU acceleration: NVIDIA GPU with CUDA support

## Advanced Testing

### Test with Multiple Documents

1. Upload 3+ documents
2. Select multiple documents (click each one)
3. Ask queries that might match different documents
4. Verify citations show correct document sources

### Test Error Handling

1. Upload invalid file (not PDF)
2. Ask query before selecting documents
3. Disconnect backend and try query
4. Check error messages display properly

### Test WebSocket Real-time

1. Monitor browser DevTools → Network → WS
2. Upload document and watch WebSocket messages
3. Verify progress updates arrive in real-time

## Cleanup

Stop all services when done:

```bash
# Stop frontend (Ctrl+C in Terminal 4)
# Stop Celery worker (Ctrl+C in Terminal 3)
# Stop backend (Ctrl+C in Terminal 2)

# Stop Docker services
docker-compose down

# Remove volumes (if desired)
docker-compose down -v
```

## Success Checklist

✅ All Docker services running
✅ Backend healthy check passes
✅ Frontend loads at localhost:5173
✅ Can upload PDF documents
✅ Documents process without errors
✅ Can ask questions and get responses
✅ Responses include citations
✅ WebSocket connects successfully
✅ All 5 services working together

## Next Steps

Once everything works:
1. Try different PDFs and queries
2. Customize frontend styling (Tailwind CSS)
3. Deploy to production
4. Add more documents for testing
5. Monitor system performance

---

**End-to-End testing guide complete!**

For issues or questions, check the logs in each terminal and review the docstrings in the code.
