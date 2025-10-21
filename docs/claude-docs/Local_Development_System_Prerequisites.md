# 🎯 **COMPLETE PRE-REQUISITES CHECKLIST FOR LOCAL DEVELOPMENT**

Before you start building the SOP Compliance RAG MVP, ensure you have **ALL** of these installed and configured on your local machine:

---

## **1. CORE SYSTEM REQUIREMENTS**

### **Hardware Requirements**
```
✅ CPU: 4+ cores (8+ recommended)
✅ RAM: 16GB minimum (32GB recommended for smooth operation)
✅ Storage: 30GB+ free disk space
   - 10GB for Ollama models
   - 10GB for Docker images/containers
   - 10GB for application data & documents
✅ GPU: Optional (NVIDIA with CUDA for faster inference)
```

### **Operating System**
```
✅ macOS: 11.0+ (Big Sur or later)
✅ Linux: Ubuntu 20.04+, Debian 11+, or equivalent
✅ Windows: Windows 10/11 with WSL2 enabled
```

---

## **2. DOCKER & CONTAINERIZATION**

### **Docker Desktop** (All platforms)
```bash
# Install Docker Desktop
# macOS: https://docs.docker.com/desktop/install/mac-install/
# Windows: https://docs.docker.com/desktop/install/windows-install/
# Linux: https://docs.docker.com/desktop/install/linux-install/

# Verify installation
docker --version
# Expected: Docker version 24.0.0 or higher

docker-compose --version
# Expected: Docker Compose version v2.20.0 or higher
```

**Post-Install Configuration**:
```bash
# Increase Docker resources (Docker Desktop → Settings → Resources)
✅ CPUs: 4+
✅ Memory: 8GB+
✅ Swap: 2GB
✅ Disk: 60GB+

# Test Docker
docker run hello-world
```

---

## **3. OLLAMA (CRITICAL - LOCAL LLM/VISION MODELS)**

### **Install Ollama**
```bash

#check WSL version
wsl.exe --list --verbose

#In WSL Ubuntu Terminal Install Ollama

# macOS & Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows (WSL2)
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
# Expected: ollama version 0.1.0 or higher

# Start Ollama service
ollama serve
# Should show: "Ollama is running on http://localhost:11434"
```

### **Pull Required Models** (THIS WILL TAKE TIME - ~15-20GB download)
```bash
# LLM Model (Primary)
ollama pull llama3.1:8b
# Size: ~4.7GB
# Time: 5-10 minutes depending on connection

# Vision Model (Primary - for diagrams/flowcharts)
ollama pull bakllava:7b
# Size: ~4.5GB
# Time: 5-10 minutes

# Vision Model (Fallback - faster, lighter)
ollama pull moondream2
# Size: ~1.8GB
# Time: 2-5 minutes

# Verify models are installed
ollama list
# Expected output:
# NAME              ID              SIZE      MODIFIED
# llama3.1:8b       xxx             4.7 GB    X minutes ago
# bakllava:7b       xxx             4.5 GB    X minutes ago
# moondream2        xxx             1.8 GB    X minutes ago
```

### **Test Ollama Models**
```bash
# Test LLM
ollama run llama3.1:8b "Hello, what is 2+2?"
# Expected: Should return "4" or similar response

# Test Vision (save a test image first)
ollama run bakllava:7b "Describe this image" --image test.jpg
# Expected: Should describe the image

# Check Ollama API
curl http://localhost:11434/api/tags
# Expected: JSON response with model list
```

---

## **4. PYTHON ENVIRONMENT**

### **Python 3.11+**
```bash
# Check Python version
python3 --version
# Expected: Python 3.11.0 or higher

# If not installed:
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Windows (via python.org or Microsoft Store)
# Download from: https://www.python.org/downloads/
```

### **pip & Virtual Environment Tools**
```bash
# Verify pip
pip3 --version
# Expected: pip 23.0+ from python 3.11

# Install virtualenv
pip3 install virtualenv

# Verify
virtualenv --version
```

### **Poetry (Optional but Recommended)**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Verify
poetry --version
# Expected: Poetry version 1.7.0 or higher
```

---

## **5. NODE.JS & NPM (FOR FRONTEND)**

### **Node.js 18+**
```bash
# Check Node version
node --version
# Expected: v18.0.0 or higher

# Check npm version
npm --version
# Expected: 9.0.0 or higher

# If not installed:
# macOS (using Homebrew)
brew install node@18

# Ubuntu/Debian (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# Download from: https://nodejs.org/
```

### **Verify Installation**
```bash
# Test npm
npm --version

# Test npx
npx --version
```

---

## **6. GOOGLE DRIVE API SETUP** (For Document Sync)

### **Step 1: Create Google Cloud Project**
```
1. Go to: https://console.cloud.google.com/
2. Create new project: "SOP-RAG-MVP"
3. Wait for project creation (30 seconds)
```

### **Step 2: Enable Google Drive API**
```
1. In project dashboard → "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click "Enable"
4. Wait for activation
```

### **Step 3: Create Service Account**
```
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: "sop-rag-service"
4. Role: "Editor" or "Viewer" (based on needs)
5. Click "Done"
```

### **Step 4: Generate JSON Key**
```
1. Click on created service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Download file (will be named: project-id-xxxxx.json)
6. Rename to: google-drive-sa.json
7. Save location for later: backend/credentials/google-drive-sa.json
```

### **Step 5: Create Drive Folder & Share**
```
1. Create folder in Google Drive: "SOP-Documents"
2. Right-click → "Share"
3. Add service account email (found in JSON: "client_email")
   Format: sop-rag-service@project-id.iam.gserviceaccount.com
4. Give "Editor" permission
5. Copy Folder ID from URL:
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
6. Save FOLDER_ID for later
```

---

## **7. DROPBOX API SETUP** (Alternative to Google Drive)

### **Step 1: Create Dropbox App**
```
1. Go to: https://www.dropbox.com/developers/apps
2. Click "Create app"
3. Choose "Scoped access"
4. Choose "Full Dropbox" access
5. Name: "SOP-RAG-MVP"
6. Click "Create app"
```

### **Step 2: Generate Access Token**
```
1. In app settings → "OAuth 2"
2. Click "Generate" under "Generated access token"
3. Copy token (starts with "sl.")
4. Save for later
```

### **Step 3: Set Permissions**
```
1. Go to "Permissions" tab
2. Enable:
   ✅ files.metadata.read
   ✅ files.content.read
   ✅ files.content.write
3. Click "Submit"
```

### **Step 4: Create Folder**
```
1. In Dropbox, create folder: "/SOPs"
2. Upload test PDFs here
3. Note folder path: /SOPs
```

---

## **8. DEVELOPMENT TOOLS**

### **Git**
```bash
# Verify Git
git --version
# Expected: git version 2.30.0 or higher

# If not installed:
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# Windows
# Download from: https://git-scm.com/
```

### **Code Editor - VS Code (Recommended)**
```bash
# Download from: https://code.visualstudio.com/

# Install recommended extensions:
- Python (Microsoft)
- Pylance
- Docker
- ES7+ React/Redux/React-Native snippets
- Prettier
- ESLint
- Tailwind CSS IntelliSense
```

### **Postman or Thunder Client** (For API Testing)
```bash
# Postman
# Download from: https://www.postman.com/downloads/

# OR Thunder Client (VS Code extension)
# Install from VS Code Extensions marketplace
```

---

## **9. SYSTEM DEPENDENCIES (LINUX/WSL)**

### **Ubuntu/Debian**
```bash
sudo apt update
sudo apt install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    python3-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    pkg-config \
    poppler-utils \
    tesseract-ocr
```

### **macOS**
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install \
    postgresql \
    redis \
    poppler \
    tesseract
```

---

## **10. OPTIONAL BUT RECOMMENDED**

### **Database Clients**
```bash
# PostgreSQL Client
# DBeaver: https://dbeaver.io/download/
# pgAdmin: https://www.pgadmin.org/download/

# Redis Client
# Redis Insight: https://redis.com/redis-enterprise/redis-insight/
# RedisInsight: https://redis.io/insight/
```

### **GPU Acceleration (Optional - Significant Speed Up)**
```bash
# For NVIDIA GPUs
# 1. Install NVIDIA Drivers
# 2. Install CUDA Toolkit 11.8+
# 3. Install cuDNN

# Verify CUDA
nvidia-smi
# Should show GPU info

# Verify PyTorch can use GPU
python3 -c "import torch; print(torch.cuda.is_available())"
# Expected: True
```

---

## **11. VALIDATION CHECKLIST** ✅

Run these commands to verify everything is ready:

```bash
#!/bin/bash
# validation.sh

echo "🔍 Validating Prerequisites..."

# Docker
echo -n "Docker: "
docker --version && echo "✅" || echo "❌ MISSING"

# Docker Compose
echo -n "Docker Compose: "
docker-compose --version && echo "✅" || echo "❌ MISSING"

# Ollama
echo -n "Ollama: "
ollama --version && echo "✅" || echo "❌ MISSING"

# Ollama Models
echo "Ollama Models:"
ollama list

# Python
echo -n "Python 3.11+: "
python3 --version | grep -q "3.1[1-9]" && echo "✅" || echo "❌ WRONG VERSION"

# Node.js
echo -n "Node.js 18+: "
node --version | grep -q "v1[8-9]" && echo "✅" || echo "❌ WRONG VERSION"

# npm
echo -n "npm: "
npm --version && echo "✅" || echo "❌ MISSING"

# Git
echo -n "Git: "
git --version && echo "✅" || echo "❌ MISSING"

# Check Ollama is running
echo -n "Ollama Service: "
curl -s http://localhost:11434/api/tags > /dev/null && echo "✅ RUNNING" || echo "⚠️  NOT RUNNING (start with: ollama serve)"

# Check disk space
echo -n "Disk Space: "
df -h . | awk 'NR==2 {if ($4+0 > 30) print "✅ " $4 " available"; else print "❌ Only " $4 " available (need 30GB+)"}'

# Check RAM
echo -n "RAM: "
free -g | awk 'NR==2 {if ($2+0 > 15) print "✅ " $2 "GB total"; else print "⚠️  Only " $2 "GB (recommended 16GB+)"}'

echo ""
echo "📋 Configuration Files Needed:"
echo "   - Google Drive credentials: backend/credentials/google-drive-sa.json"
echo "   - Environment file: backend/.env"
echo "   - Environment file: frontend/.env"
echo ""
echo "📝 Next Steps:"
echo "   1. Setup Google Drive/Dropbox API (see sections above)"
echo "   2. Clone/create project directory"
echo "   3. Place credentials in correct locations"
echo "   4. Run ./setup.sh"
```

---

## **12. FINAL PRE-FLIGHT CHECKLIST**

Before running `./setup.sh`, ensure:

```
✅ Docker Desktop is running
✅ Ollama service is running (ollama serve)
✅ All 3 Ollama models are downloaded
✅ Google Drive service account JSON is ready
✅ Google Drive folder ID is noted
✅ At least 30GB free disk space
✅ At least 16GB RAM available
✅ Python 3.11+ installed
✅ Node.js 18+ installed
✅ Git installed
✅ Internet connection active (for downloads)
```

---

## **13. ESTIMATED SETUP TIME**

```
⏱️  Total Setup Time: 45-60 minutes

Breakdown:
- Docker installation: 10 min
- Ollama installation: 5 min
- Ollama model downloads: 20-30 min
- Google Drive API setup: 10 min
- System dependencies: 5 min
- Validation: 5 min
```

---

## **🎯 READY TO START?**

Once ALL prerequisites are met, you can proceed with:

```bash
# Clone repository
git clone <your-repo-url>
cd sop-rag-multimodal-mvp

# Run validation
chmod +x validation.sh
./validation.sh

# If all checks pass ✅
chmod +x setup.sh
./setup.sh
```

---