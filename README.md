# SOP RAG MVP - Multimodal Retrieval-Augmented Generation System

A production-grade, locally-runnable multimodal RAG system for SOP compliance with full PDF understanding, vision-powered diagram comprehension, and high-accuracy table extraction.

## Features

- **Full PDF Understanding**: Text + Images + Complex Tables
- **Vision-Powered**: Diagram/flowchart comprehension via Ollama vision models
- **High Table Accuracy**: Multiple extraction strategies with validation
- **Sub-30s Retrieval**: Aggressive caching and optimization
- **2-5min Processing**: Background jobs with progress tracking UI
- **Multi-Modal Embeddings**: Text, images, and tables in unified vector space
- **Real-Time Updates**: WebSocket-based processing progress
- **Production Ready**: Docker containerization and scalable architecture

## Architecture

### Technology Stack

**Backend:**
- Framework: FastAPI + Celery
- Database: PostgreSQL
- Cache: Redis
- Vector Store: ChromaDB
- Object Storage: MinIO
- Task Queue: Celery + Redis

**AI/ML:**
- Text Embeddings: BAAI/bge-base-en-v1.5
- Vision Models: bakllava:7b (primary), moondream2 (fallback)
- Image Embeddings: openai/clip-vit-base-patch32
- LLM: llama3.1:8b (primary), mistral:7b (fallback)
- Reranker: BAAI/bge-reranker-base

**Frontend:**
- Framework: React 18 + TypeScript
- UI Library: shadcn/ui + Tailwind CSS
- State Management: Zustand
- Data Fetching: TanStack Query

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Ollama (for local LLM and vision models)
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Installation & Setup

1. **Clone repository and setup environment:**
```bash
cd /home/dabhi/projects/sop-rag-mvp
cp .env.example .env
# Edit .env with your configuration
```

2. **Install and run Ollama models:**
```bash
# Install Ollama from https://ollama.com/
ollama pull llama3.1:8b
ollama pull bakllava:7b
ollama pull moondream2
```

3. **Start services with Docker Compose:**
```bash
docker-compose up -d
```

4. **Backend setup (for local development):**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

5. **Frontend setup (for local development):**
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
sop-rag-mvp/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/              # Core business logic
│   │   ├── services/          # External service integrations
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/v1/            # API routes
│   │   ├── tasks/             # Celery tasks
│   │   └── utils/             # Utilities
│   ├── tests/                 # Test suite
│   ├── data/                  # Local storage (ChromaDB, PostgreSQL, MinIO)
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API services
│   │   ├── stores/            # Zustand stores
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utilities
│   └── package.json           # Node dependencies
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   ├── PROCESSING.md          # Processing pipeline
│   ├── DEPLOYMENT.md          # Deployment guide
│   └── TROUBLESHOOTING.md     # Common issues
├── docker-compose.yml         # Production docker compose
├── docker-compose.dev.yml     # Development overrides
└── .env.example              # Environment template
```

## API Endpoints

### Query Endpoint
```
POST /api/v1/query
```

### Document Management
```
POST /api/v1/documents/upload
GET /api/v1/documents
DELETE /api/v1/documents/{id}
```

### Processing Status
```
GET /api/v1/processing/{task_id}
```

See API.md for complete documentation.

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Quality
```bash
black backend/
flake8 backend/
mypy backend/
```

### Building Docker Images
```bash
docker-compose build
```

## Deployment

See DEPLOYMENT.md for production deployment guide.

## Troubleshooting

Common issues and solutions are documented in TROUBLESHOOTING.md

## License

Proprietary - All Rights Reserved
