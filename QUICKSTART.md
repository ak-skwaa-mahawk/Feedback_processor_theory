# Feedback Processor Theory - Quick Start Guide

Get up and running in **5 minutes** with the Harmonic Demo multi-LLM streaming platform.

---

## Prerequisites

- **Docker** and **Docker Compose** (recommended), OR
- **Python 3.10+** with pip
- **OpenAI API key** (required)
- Optional: NVIDIA NIM key, Anthropic key

---

## Option 1: Docker Deployment (Recommended)

### Step 1: Clone and Setup

```bash
git clone https://github.com/ak-skwaa-mahawk/Feedback_processor_theory.git
cd Feedback_processor_theory/harmonic-demo

# Copy environment template
cp .env.example .env
```

### Step 2: Configure API Keys

Edit `.env` and add your keys:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional (remove or leave empty if not using)
NVAPI_KEY=nvapi-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 4: Access

Open your browser to: **http://localhost:8000**

---

## Option 2: Manual Setup

### Step 1: Backend Setup

```bash
cd harmonic-demo/backend

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="sk-proj-your-key-here"
export ENABLE_EMBEDDINGS=true
export DEMO_MODE=false

# Start server
python server.py
```

### Step 2: Frontend Setup

Open a new terminal:

```bash
cd harmonic-demo/frontend

# Serve frontend
python -m http.server 8000
```

### Step 3: Access

Open your browser to: **http://localhost:8000**

---

## First Test

1. Click **Connect** - should see "Connected" status
2. Select **GPT** from LLM dropdown
3. Type: `Count to 10`
4. Click **Send** - watch tokens stream in real-time
5. Check the resonance meter (if audio enabled)

---

## Feature Modes

### Demo Mode (No API Costs)

```bash
# In .env
DEMO_MODE=true
ENABLE_EMBEDDINGS=false
ENABLE_AUDIO=false
```

Uses simulated embeddings - perfect for testing UI/UX without API costs.

### Production Mode (Full Features)

```bash
# In .env
DEMO_MODE=false
ENABLE_EMBEDDINGS=true
ENABLE_AUDIO=true
USE_EMBEDDING_CACHE=true
```

Real OpenAI embeddings with caching to reduce costs.

---

## Testing Your Setup

### Test Backend Health

```bash
# Check WebSocket is responding
wscat -c ws://localhost:8765

# Or use curl (if health endpoint implemented)
curl http://localhost:8765/health
```

### Run Test Suite

```bash
cd backend
pytest tests/ -v
```

### Test Individual LLM Clients

```bash
cd backend
python llm_clients.py
```

This will test each configured LLM client.

---

## Common Issues

### "OPENAI_API_KEY not set"

**Solution:** Make sure `.env` exists and contains your key:
```bash
cat .env | grep OPENAI_API_KEY
```

### "Connection refused" when accessing frontend

**Solution:** Check