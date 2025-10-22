# Frontend Integration Guide

## Overview

The React frontend is now ready to use with the backend API. This document explains how to run and test the complete system.

## Running the Complete System

### 1. Start Backend Services

```bash
# Terminal 1: Start Docker services
cd /home/dabhi/projects/sop-rag-mvp
docker-compose up -d

# Terminal 2: Start FastAPI backend
cd backend
python app/main.py

# Terminal 3: Start Celery worker
cd backend
python celery_worker.py
```

### 2. Start Frontend

```bash
# Terminal 4: Start React frontend
cd frontend
npm install  # (first time only)
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Features Demonstrated

### Document Management
1. Navigate to "Documents" tab
2. Click "Upload Document"
3. Select a PDF file from your computer
4. Wait for processing to complete (status changes to "completed")
5. You should see chunks count (text, images, tables)

### Chat with Documents
1. Go to "Chat" tab
2. Click on a document card to select it (shows blue highlight)
3. Type a question about the document
4. Press Enter or click Send
5. View the AI response with citations

### Real-time Updates
- WebSocket automatically connects
- Processing progress updates appear in real-time
- Document status updates reflect backend processing

## API Endpoints Used by Frontend

### Document Endpoints
```
POST   /api/v1/documents/upload    - Upload PDF
GET    /api/v1/documents           - List documents
DELETE /api/v1/documents/{id}      - Delete document
```

### Query Endpoints
```
POST   /api/v1/query               - Submit query with RAG
GET    /api/v1/query/health        - Check RAG service
```

### WebSocket
```
WS     /ws                         - Real-time updates
```

## Troubleshooting

### Frontend won't connect to backend
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS is enabled in backend
3. Verify API base URL in frontend/src/services/api.ts

### Documents won't upload
1. Ensure file is PDF format
2. Check backend storage has write permissions
3. Verify Celery worker is running
4. Check PostgreSQL is running

### No search results in chat
1. Ensure document processing is complete
2. Check vector store has chunks indexed
3. Verify ChromaDB is accessible
4. Try refreshing documents list

### WebSocket connection fails
1. Check ws:// protocol is used (not wss://)
2. Ensure backend WebSocket handler is active
3. Check browser console for specific errors

## Performance Tips

1. **Caching**: Query results are cached in Redis
2. **Batch Processing**: Upload multiple documents at once
3. **Browser DevTools**: Monitor network tab to see API calls
4. **Production Build**: Run `npm run build` for optimized version

## Development

### Adding New Components

1. Create component in `src/components/`
2. Use TypeScript for type safety
3. Export from component index (if needed)
4. Import and use in App.tsx or other components

### Adding New API Endpoints

1. Add method to `src/services/api.ts`
2. Define types in `src/types/index.ts`
3. Use store or component state to manage response
4. Handle errors gracefully

### Testing Locally

```bash
# Type checking
npm run type-check

# Build verification
npm run build

# Linting
npm run lint
```

## Next Steps

1. **Customize Styling**: Modify Tailwind classes in components
2. **Add Features**: Extend chat functionality (file preview, export results)
3. **Deployment**: Build with `npm run build`, serve from any static host
4. **Authentication**: Add auth to backend and wire up in frontend

## Project Structure

```
frontend/
├── src/
│   ├── components/        - React UI components
│   ├── services/          - API client (api.ts)
│   ├── stores/            - Zustand state (chat, documents)
│   ├── types/             - TypeScript interfaces
│   ├── App.tsx            - Main app layout
│   └── main.tsx           - Entry point
├── vite.config.ts         - Vite build config
├── tailwind.config.js     - Tailwind CSS config
└── package.json           - Dependencies
```

## Browser Console

Monitor the console for:
- API request/response logs
- WebSocket connection logs
- Error messages and stack traces
- Performance metrics

## Backend Integration Points

### Document Upload Flow
```
Frontend → POST /api/v1/documents/upload
Backend → Save file, queue Celery task
Backend → Extract text, chunks, embeddings
Backend → Index in ChromaDB
Frontend → Poll /api/v1/documents (or get WebSocket update)
```

### Query Flow
```
Frontend → POST /api/v1/query
Backend → Generate embedding
Backend → Search ChromaDB
Backend → Rerank results
Backend → Generate LLM response
Backend → Return with citations
Frontend → Display response + sources
```

## Success Indicators

✅ Frontend loads without errors
✅ Can upload PDF documents
✅ Documents show processing progress
✅ Can see document chunks after processing
✅ Can select documents and ask questions
✅ Receive answers with citations
✅ WebSocket shows real-time updates

---

**The frontend is fully integrated with the backend RAG system.**

