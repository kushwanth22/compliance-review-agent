# Compliance Review Agent

> **POC 0** — Zero-cost local AI compliance review for Microsoft Global Ads
>
> [![CI](https://github.com/kushwanth22/compliance-review-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/kushwanth22/compliance-review-agent/actions/workflows/ci.yml)
> [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
>
> ## Overview
>
> Automated multi-domain compliance review agent for Microsoft Global Ads creative assets. Reviews PNG, JPEG, GIF, HTML5, MP4, PDF, DOCX, and PPTX files against Brand, Legal/CELA, Accessibility, Global Readiness, and Product Marketing standards.
>
> **Produces:** Pass/fail decisions with severity scoring, written rationale, grounded citations, and human escalation triggers.
>
> ## Architecture
>
> ```
> Asset Upload → Ingestion → RAG Retrieval → Multi-Agent Review (async) → Compliance Report
>                                                ├── Brand Agent
>                                                ├── Legal/CELA Agent
>                                                ├── Accessibility Agent
>                                                ├── Global Readiness Agent
>                                                └── Product Marketing Agent
> ```
>
> All domain agents run **concurrently** via `asyncio.gather()`.
>
> ## Phase Roadmap
>
> | Phase | Stack | Cost | Status |
> |---|---|---|---|
> | **POC 0** | Ollama + ChromaDB + SQLite + Docker Compose | **$0** | Active |
> | **POC 1** | Azure OpenAI + Azure AI Search + Container Apps | ~$200 credits | Next |
> | **Production** | AKS + GPT-4o + Azure AI Search Standard | Microsoft funded | Future |
>
> **POC 0 → POC 1 is a config-only swap** — only `.env` changes, no code changes needed.
>
> ## Tech Stack (POC 0 — Zero Cost)
>
> | Layer | Technology |
> |---|---|
> | API | FastAPI + Uvicorn (async) |
> | LLM | [Ollama](https://ollama.com) + llama3 (local) via **LiteLLM** |
> | Embeddings | Ollama nomic-embed-text (local) |
> | Vector Store | ChromaDB (local file-based) |
> | Database | SQLite + SQLAlchemy async + Alembic |
> | Validation | Pydantic v2 |
> | Logging | structlog (JSON) |
> | Testing | pytest + pytest-asyncio |
> | Package Manager | [uv](https://github.com/astral-sh/uv) |
> | Containers | Docker + Docker Compose |
> | CI | GitHub Actions (free) |
> | IaC | OpenTofu (ready for POC 1) |
>
> ## Quick Start
>
> ### Prerequisites
> - Docker Desktop
> - - [Ollama](https://ollama.com/download) installed locally
>   - - [uv](https://github.com/astral-sh/uv) installed
>    
>     - ### 1. Clone and setup
>    
>     - ```bash
>       git clone https://github.com/kushwanth22/compliance-review-agent.git
>       cd compliance-review-agent
>       cp .env.example .env
>       ```
>
> ### 2. Pull Ollama models (one-time, free)
>
> ```bash
> ollama pull llama3
> ollama pull nomic-embed-text
> ```
>
> ### 3. Start the stack
>
> ```bash
> docker compose up
> ```
>
> API available at: http://localhost:8000
> Swagger docs at: http://localhost:8000/docs
>
> ### 4. Run locally without Docker
>
> ```bash
> uv sync --dev
> uv run uvicorn api.app:app --reload
> ```
>
> ## API Endpoints
>
> | Method | Endpoint | Description |
> |---|---|---|
> | GET | `/health` | Health check |
> | POST | `/api/v1/assets` | Upload creative asset |
> | POST | `/api/v1/reviews` | Trigger compliance review |
> | GET | `/api/v1/reports/{id}` | Get compliance report |
>
> ## Development
>
> ```bash
> # Install dependencies
> uv sync --dev
>
> # Run tests
> uv run pytest tests/ -v
>
> # Lint
> uv run ruff check .
>
> # Format
> uv run ruff format .
>
> # Run DB migrations
> uv run alembic upgrade head
> ```
>
> ## Project Structure
>
> ```
> compliance-review-agent/
> ├── api/                    # FastAPI app, routes, middleware
> ├── agents/                 # Domain compliance agents (Brand, Legal, etc.)
> ├── rag/                    # Retrieval-augmented generation (ChromaDB / Azure Search)
> ├── ingestion/              # Asset parsers (PDF, DOCX, PPTX, images, video)
> ├── knowledge_base/         # Compliance guidance documents + indexing
> ├── models/                 # Pydantic + SQLAlchemy models
> ├── evaluation/             # Scoring + escalation rules
> ├── db/                     # Database session + migrations (Alembic)
> ├── config/                 # Settings (pydantic-settings) + logging
> ├── tests/                  # pytest unit + integration tests
> ├── docker/                 # Dockerfiles
> ├── infra/tofu/             # OpenTofu IaC (ready for POC 1 Azure deploy)
> └── .github/workflows/      # GitHub Actions CI (+ dormant CD for POC 1)
> ```
>
> ## Compliance Domains
>
> | Domain | Checks |
> |---|---|
> | **Brand** | Logo usage, colors, typography, visual identity |
> | **Legal/CELA** | Disclaimers, claims, regulatory compliance |
> | **Accessibility** | WCAG 2.1 AA, alt text, color contrast, captions |
> | **Global Readiness** | Localization, cultural sensitivity, regional restrictions |
> | **Product Marketing** | Feature accuracy, messaging alignment, campaign standards |
>
> ## Contributing
>
> 1. Create a feature branch: `git checkout -b feature/your-feature`
> 2. 2. Make changes and run tests: `uv run pytest`
>    3. 3. Lint: `uv run ruff check . && uv run ruff format .`
>       4. 4. Open a PR against `main`
>         
>          5. ## License
>         
>          6. MIT — see [LICENSE](LICENSE)
