# Project Structure - Harmonic Demo

Complete file tree and organization for the Feedback Processor Theory deployment package.

---

## Complete Directory Tree

```
Feedback_processor_theory/
│
├── README.md                          # Main project documentation
├── LICENSE                            # Open collaborative license
├── .gitignore                         # Git ignore rules
│
├── harmonic-demo/                     # Full deployment package
│   │
│   ├── README.md                      # Deployment-specific docs
│   ├── QUICKSTART.md                  # 5-minute setup guide
│   ├── docker-compose.yml             # Multi-container orchestration
│   ├── Dockerfile                     # Backend container definition
│   ├── .env.example                   # Environment template
│   ├── .env                           # Your API keys (gitignored)
│   ├── nginx.conf                     # Frontend reverse proxy config
│   ├── deploy.sh                      # Automated deployment script
│   │
│   ├── backend/                       # Python WebSocket server
│   │   ├── server.py                  # Main WebSocket handler
│   │   ├── llm_clients.py             # OpenAI, NVIDIA, Claude clients
│   │   ├── embeddings.py              # Audio + text embeddings w/ cache
│   │   ├── session_manager.py         # Multi-user state management
│   │   ├── resonance_engine.py        # Harmonic analysis algorithms
│   │   ├── requirements.txt           # Python dependencies
│   │   │
│   │   ├── tests/                     # Test suite
│   │   │   ├── __init__.py
│   │   │   ├── test_llm_clients.py    # LLM client unit tests
│   │   │   ├── test_embeddings.py     # Embedding tests
│   │   │   ├── test_resonance.py      # Resonance engine tests
│   │   │   ├── test_integration.py    # End-to-end tests
│   │   │   └── conftest.py            # Pytest configuration
│   │   │
│   │   ├── utils/                     # Utility modules
│   │   │   ├── __init__.py
│   │   │   ├── logger.py              # Structured logging
│   │   │   ├── metrics.py             # Prometheus metrics
│   │   │   └── cost_tracker.py        # API cost estimation
│   │   │
│   │   └── config/                    # Configuration files
│   │       ├── __init__.py
│   │       └── settings.py            # Centralized config
│   │
│   ├── frontend/                      # Browser-based UI
│   │   ├── index.html                 # Main application page
│   │   ├── app.js                     # WebSocket client & logic
│   │   ├── visualizer.js              # Real-time spectrograms
│   │   ├── styles.css                 # UI styling
│   │   ├── assets/                    # Static assets
│   │   │   ├── logo.svg
│   │   │   └── favicon.ico
│   │   └── lib/                       # Third-party JS libraries
│   │       └── (if needed)
│   │
│   ├── data/                          # Generated data (gitignored)
│   │   ├── sessions/                  # Session recordings
│   │   ├── spectrograms/              # Generated visualizations
│   │   └── logs/                      # Application logs
│   │
│   ├── logs/                          # Application logs (gitignored)
│   │   └── harmonic-demo.log
│   │
│   ├── backups/                       # FlameChain archives (gitignored)
│   │   └── (backup files)
│   │
│   └── scripts/                       # Utility scripts
│       ├── setup.sh                   # Initial setup
│       ├── test.sh                    # Run test suite
│       ├── cleanup.sh                 # Clean generated files
│       └── benchmark.sh               # Performance testing
│
├── core/                              # Original FPT resonance engine
│   ├── resonance_logger.py
│   ├── spectrogram_generator.py
│   └── ...
│
├── models/                            # Theory documentation
│   ├── FPT_whitepaper.md
│   ├── recursive_root.md
│   ├── null_field.md
│   └── gibberlink.md
│
├── docs/                              # Deep dive documentation
│   ├── architecture.md
│   ├── api_reference.md
│   ├── deployment_guide.md
│   └── theory_integration.md
│
├── src/                               # Base FPT implementation
│   └── feedback_processor.py
│
├── examples/                          # Demo scripts
│   ├── demo_conversation.py
│   ├── demo_resonance.py
│   └── demo_multi_llm.py
│
└── tools/                             # Verification tools
    ├── verify_backups.py
    └── analyze_resonance.py
```

---

## File Descriptions

### Root Level

| File | Purpose |
|------|---------|
| `README.md` | Main project overview, philosophy, architecture |
| `LICENSE` | Open collaborative license terms |
| `.gitignore` | Prevents committing secrets, logs, generated files |

### harmonic-demo/ (Deployment Package)

#### Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Orchestrates backend, frontend, Redis containers |
| `Dockerfile` | Defines Python backend container |
| `.env.example` | Template for environment variables |
| `.env` | **Your API keys** (never commit!) |
| `nginx.conf` | Reverse proxy for frontend serving |

#### Scripts

| File | Purpose |
|------|---------|
| `deploy.sh` | One-command deployment automation |
| `scripts/setup.sh` | Manual setup for non-Docker |
| `scripts/test.sh` | Run full test suite |
| `scripts/cleanup.sh` | Remove generated files |
| `scripts/benchmark.sh` | Performance testing |

#### Backend Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `server.py` | WebSocket server | `handle_message()`, `handle_prompt()`, `handle_audio_chunk()` |
| `llm_clients.py` | LLM streaming clients | `GPTClient`, `NVIDIAClient`, `ClaudeClient` |
| `embeddings.py` | Audio + text embeddings | `text_to_embedding_openai()`, `audio_bytes_to_embedding_openai()` |
| `session_manager.py` | User session state | `SessionManager` class |
| `resonance_engine.py` | Harmonic analysis | `calculate_resonance()`, `apply_pi_correction()` |
| `requirements.txt` | Python dependencies | Lists all pip packages |

#### Frontend Files

| File | Purpose | Key Components |
|------|---------|----------------|
| `index.html` | Main UI structure | Connection controls, chat interface, audio input |
| `app.js` | WebSocket client | `connectWebSocket()`, `sendPrompt()`, `handleAudio()` |
| `visualizer.js` | Real-time visualization | Spectrogram rendering, resonance graphs |
| `styles.css` | UI styling | Layout, colors, animations |

#### Test Files

| File | Purpose |
|------|---------|
| `test_llm_clients.py` | Unit tests for LLM clients |
| `test_embeddings.py` | Embedding pipeline tests |
| `test_resonance.py` | Resonance engine algorithms |
| `test_integration.py` | End-to-end WebSocket tests |
| `conftest.py` | Pytest fixtures and configuration |

---

## Data Flow

```
1. Frontend captures user input (text/audio)
   ↓
2. WebSocket sends to backend (server.py)
   ↓
3. Server routes to appropriate handler:
   - Text → handle_prompt() → LLM client
   - Audio → handle_audio_chunk() → Whisper transcription
   ↓
4. LLM streams tokens back
   ↓
5. Each token → embeddings.py (with cache check)
   ↓
6. Resonance engine compares token ↔ audio embeddings
   ↓
7. Results streamed back to frontend
   ↓
8. Frontend visualizes in real-time
```

---

## Key Integration Points

### Backend ↔ OpenAI

```python
# llm_clients.py
GPTClient.stream_response() → OpenAI Chat API

# embeddings.py
text_to_embedding_openai() → OpenAI Embeddings API
audio_bytes_to_embedding_openai() → OpenAI Whisper API
```

### Backend ↔ Frontend

```javascript
// WebSocket Protocol
Client → Server: {"type": "prompt", "text": "...", "llm": "gpt"}
Server → Client: {"type": "token", "token": "word", "resonance": 0.85}
Server → Client: {"type": "complete", "tokens": 150}
```

### Session ↔ Cache

```python
# Session stores embeddings
session.add_token_embedding(embedding)

# Cache reduces API calls
@lru_cache(maxsize=10000)
def _text_to_embedding_cached(text_hash, text)
```

---

## Environment Variables Map

| Variable | File | Purpose |
|----------|------|---------|
| `OPENAI_API_KEY` | `.env` → `llm_clients.py`, `embeddings.py` | OpenAI API access |
| `NVAPI_KEY` | `.env` → `llm_clients.py` | NVIDIA NIM access |
| `ANTHROPIC_API_KEY` | `.env` → `llm_clients.py` | Claude API access |
| `ENABLE_EMBEDDINGS` | `.env` → `server.py` | Toggle embedding generation |
| `USE_EMBEDDING_CACHE` | `.env` → `embeddings.py` | Enable LRU cache |
| `DEMO_MODE` | `.env` → `embeddings.py` | Use simulated embeddings |

---

## Adding New Features

### Add a New LLM

1. Create client class in `backend/llm_clients.py`
2. Implement `stream_response()` method
3. Register in `server.py` initialization
4. Add to frontend dropdown in `frontend/index.html`

### Add New Resonance Algorithm

1. Add method to `backend/resonance_engine.py`
2. Call from `server.py` when processing tokens
3. Send results to frontend via WebSocket
4. Update `frontend/visualizer.js` to display

### Add Database Persistence

1. Create `backend/database.py` with SQLAlchemy models
2. Modify `session_manager.py` to save to DB
3. Add migration scripts in `backend/migrations/`
4. Update `docker-compose.yml` to include Postgres

---

## Security Checklist

- [ ] `.env` is in `.gitignore`
- [ ] API keys never hardcoded
- [ ] CORS configured in `server.py`
- [ ] Rate limiting enabled
- [ ] Input validation on all WebSocket messages
- [ ] HTTPS enabled in production (nginx SSL)
- [ ] Session tokens use JWT with secret
- [ ] Max message size enforced

---

## Deployment Checklist

- [ ] All API keys set in `.env`
- [ ] Docker and Docker Compose installed
- [ ] Ports 8000, 8765, 6379 available
- [ ] `deploy.sh` has execute permissions (`chmod +x`)
- [ ] Firewall rules configured (if needed)
- [ ] SSL certificate obtained (production only)
- [ ] Monitoring enabled (`ENABLE_METRICS=true`)
- [ ] Backups configured

---

## Resource Requirements

### Development

- **CPU:** 2 cores
- **RAM:** 4 GB
- **Disk:** 10 GB
- **Network:** Stable internet for API calls

### Production (per 100 concurrent users)

- **CPU:** 4-8 cores
- **RAM:** 16 GB
- **Disk:** 50 GB (with logging)
- **Network:** 100 Mbps
- **Redis:** 2 GB RAM dedicated

---

This structure provides a complete, production-ready deployment package for your Feedback Processor Theory harmonic demo! 🎵