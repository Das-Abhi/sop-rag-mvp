# Setup Instructions - SOP RAG MVP

Complete step-by-step setup guide for the SOP RAG MVP system.

## System Requirements

- **OS**: Linux, macOS, or Windows (with WSL2)
- **RAM**: 12GB minimum (16GB recommended)
- **Disk Space**: 50GB free (for models and data)
- **CPU**: 4+ cores recommended
- **GPU**: Optional (accelerates vision models)

## Installation Steps

### 1. Prerequisites Installation

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
sudo apt-get install -y nodejs npm
sudo apt-get install -y docker.io docker-compose-plugin
```

#### On macOS:
```bash
# Using Homebrew
brew install python@3.11
brew install node
brew install docker
```

### 2. Repository Setup

```bash
# Clone or navigate to project directory
cd /home/dabhi/projects/sop-rag-mvp

# Create .env from template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Ollama Setup

```bash
# Install Ollama (if not already installed)
# From: https://ollama.com/

# Ensure Ollama service is running
ollama serve &

# Pull required models
ollama pull llama3.1:8b        # ~4.7GB
ollama pull bakllava:7b        # ~4.0GB
ollama pull moondream2         # ~1.6GB

# Test models
ollama run llama3.1:8b "Hello, how are you?"
```

### 4. Docker Services Setup

```bash
# Start PostgreSQL, Redis, MinIO
docker-compose up -d postgres redis minio

# Wait for services to be healthy (30 seconds)
sleep 30

# Verify services
docker-compose ps
```

### 5. Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Initialize database
alembic upgrade head

# Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, run Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access at http://localhost:3000
```

### 7. Verify Installation

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Frontend**: Open http://localhost:3000 in browser

3. **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

4. **ChromaDB**: Automatically initialized in `backend/data/chromadb`

## Docker Compose Setup (Recommended)

For complete setup with all services:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# With development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Environment Configuration

Key environment variables in `.env`:

```
# API Settings
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sop_rag

# Cache
REDIS_HOST=localhost
REDIS_PORT=6379

# Object Storage
MINIO_HOST=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# AI Models
OLLAMA_HOST=http://localhost:11434
OLLAMA_TEXT_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=bakllava:7b
```

## First Run Workflow

1. **Upload a test document:**
   - Go to frontend http://localhost:3000
   - Click "Upload Document"
   - Select a PDF file
   - Monitor progress in processing panel

2. **Query the system:**
   - Once processing completes
   - Type a query in the chat interface
   - Review results and citations

3. **Check admin panels:**
   - MinIO: http://localhost:9001
   - PostgreSQL: Use `psql` client
   - Redis: Use `redis-cli`

## Troubleshooting

### Models not loading
```bash
# Check Ollama service
ps aux | grep ollama

# Restart Ollama
pkill ollama
ollama serve &
```

### Database connection errors
```bash
# Check PostgreSQL
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### Memory issues
```bash
# Check available memory
free -h

# Increase Docker memory limit
# Edit /etc/docker/daemon.json and increase memory allocation
```

## Next Steps

1. Review API.md for API documentation
2. See ARCHITECTURE.md for system design
3. Check PROCESSING.md for pipeline details
4. Read DEPLOYMENT.md for production setup

## Support

For issues, check TROUBLESHOOTING.md or review logs:

```bash
# Backend logs
docker-compose logs backend

# Worker logs
docker-compose logs celery_worker

# All logs
docker-compose logs -f
```
