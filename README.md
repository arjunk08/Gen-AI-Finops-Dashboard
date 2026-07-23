# Gen-AI FinOps Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)
![OpenAI SDK](https://img.shields.io/badge/?modal=icon&q=openaigym)
![Status](https://img.shields.io/badge/Status-Active-success)


An AI-powered FinOps dashboard for analyzing, visualizing, and optimizing Generative AI cloud spend. Upload invoices, track token consumption, get AI-driven cost recommendations, and forecast future usage — all from a single interface.

**Live App:** [gen-ai-finops-dashboard.streamlit.app](https://gen-ai-finops-dashboard.streamlit.app)  
**API (Render):** [gen-ai-finops-dashboard.onrender.com](https://gen-ai-finops-dashboard.onrender.com)

---

## Architecture

```
┌─────────────────────┐       HTTPS        ┌──────────────────────┐
│   Streamlit Frontend │ ◄──────────────► │   FastAPI Backend     │
│   (Streamlit Cloud)  │                    │   (Render)            │
└─────────────────────┘                    └──────────┬───────────┘
                                                      │
                                           ┌──────────┴───────────┐
                                           │                      │
                                    ┌──────▼──────┐     ┌────────▼────────┐
                                    │ PostgreSQL   │     │ ChromaDB        │
                                    │ (NeonDB)     │     │ (Persistent)    │
                                    │              │     │ Vector Store    │
                                    │              │     │         +       │
                                                         │     reranking   │
                                                         │ using Cohere API│
                                    └──────────────┘     └─────────────────┘
                                                                │
                                                      ┌────────▼────────┐
                                                      │  LLM Providers  │
                                                      │  OpenAI / Cohere│
                                                      └─────────────────┘
```

The frontend (Streamlit) communicates exclusively with the backend (FastAPI) over HTTPS. The backend handles all database operations, authentication, vector indexing, Rewriting query, Reranking & retrieval using Cohere API, and LLM calls for answer.

---

## Project Structure

```
Gen-AI-Finops-Dashboard/
├── Dashboard.py                    # Streamlit entry point — auth, upload, dashboard views
├── pages/
│   ├── 1 Key Insights.py          # Per-invoice charts: cost by model, provider, tokens
│   ├── 2 AI consultation.py       # RAG-based Q&A against user invoices
│   ├── 3 Optimization tips.py     # AI-generated cost optimization recommendations
│   └── 4 Forecasts.py             # Linear regression cost/token forecasting
├── backend/
│   ├── main.py                     # FastAPI app — mounts auth, invoice, AI routers
│   ├── auth.py                     # Password hashing (bcrypt), JWT creation & decoding
│   ├── dependancies.py             # get_db session, get_current_user dependency
│   ├── ai_protection.py            # Input validation, in-memory rate limiting
│   ├── vector_store.py             # ChromaDB: index invoice rows, query context,reranking and retrieval
│   └── routers/
│       ├── auth_router.py          # POST /auth/register, /auth/login, /auth/token
│       ├── invoice_router.py       # Upload, list, delete, reindex invoices
│       └── ai_router.py            # /ai/consult, /ai/optimize, /ai/consult/cohere, /ai/rewrite
├── db_end/
│   ├── db1.py                      # SQLAlchemy engine & session (DATABASE_URL from env)
│   ├── models.py                   # ORM models: userid, invoice, invoice_rows, chathistory, optimization_rec
│   ├── dbfunctions.py              # Standalone DB helpers (save_file, get_records)
│   └── init_db.py                  # Script to create all tables
├── tests/
│   └── test_main.py                # Pytest suite — root, auth register/login endpoints
├── Sample-data/                    # Example CSV invoices for testing uploads
├── .github/workflows/ci.yml       # GitHub Actions CI — Ruff lint + pytest
├── .streamlit/config.toml          # Streamlit theme (dark mode)
├── .devcontainer/devcontainer.json # GitHub Codespaces config
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Tech Stack

| Layer        | Technology                                                                 |
|--------------|---------------------------------------------------------------------------|
| Frontend     | **Streamlit** — multipage app with session state auth                     |
| Backend API  | **FastAPI** — REST endpoints, OAuth2 bearer token auth                    |
| ORM          | **SQLAlchemy** — declarative models, session management                   |
| Database     | **PostgreSQL** on NeonDB (production), SQLite (tests)                     |
| Vector Store | **ChromaDB & CohereAPI** — persistent client, sentence embeddings per invoice row + Retrieval & Reranking|
| LLM          | **OpenAI_SDK** (Azure-compatible endpoint) + (Groq API Using OpenAI SDK)  |
| Auth         | **bcrypt** (passlib) + **python-jose** JWT (HS256)                        |
| Visualization| **Matplotlib**, **Seaborn**, **Plotly**                                   |
| CI/CD        | **GitHub Actions** (Ruff linter + pytest), deployed to **Render** + **Streamlit Cloud** |

---

## API Endpoints

### Authentication (`/auth`)

| Method | Endpoint         | Description                              | Auth |
|--------|------------------|------------------------------------------|------|
| POST   | `/auth/register` | Create a new user account                | No   |
| POST   | `/auth/login`    | Login, returns JWT access token          | No   |
| POST   | `/auth/token`    | OAuth2-compatible login (Swagger UI)     | No   |

### Invoices (`/invoices`)

| Method | Endpoint                      | Description                                        | Auth |
|--------|-------------------------------|----------------------------------------------------|------|
| POST   | `/invoices/upload-invoice`    | Upload CSV/XLSX/JSON, parse and store rows          | Yes  |
| GET    | `/invoices/my-invoices`       | List all invoices for the current user              | Yes  |
| GET    | `/invoices/dashboard-summary` | Aggregated cost, tokens, pay cycle across invoices  | Yes  |
| GET    | `/invoices/models-summary`    | Distinct models and providers used                  | Yes  |
| GET    | `/invoices/{invoice_id}`      | Full invoice detail with all parsed rows            | Yes  |
| DELETE | `/invoices/del/{invoice_id}`  | Delete an invoice and its rows                      | Yes  |
| POST   | `/invoices/reindex`           | Re-index all invoice rows into ChromaDB             | Yes  |
| GET    | `/invoices/chat/{invoice_id}` | Retrieve chat history for an invoice                | Yes  |

### AI Consultation (`/ai`)

| Method | Endpoint              | Description                                          | Auth |
|--------|-----------------------|------------------------------------------------------|------|
| POST   | `/ai/consult`         | RAG Q&A — retrieves context from ChromaDB, calls OpenAI | Yes  |
| POST   | `/ai/optimize`        | Generate & cache cost optimization recommendations   | Yes  |
| POST   | `/ai/consult/cohere`  | Same as consult, routed through Cohere Command R7B   | Yes  |
| POST   | `/ai/rewrite`         | Rewrite user question into retrieval keywords (Cohere) | Yes  |

---

## RAG Pipeline

1. **Upload** — Invoice CSV/XLSX is parsed with Pandas. Columns are fuzzy-matched to a standard schema (amount, tokens, model, provider, etc.).
2. **Index** — Each parsed row is serialized into a natural-language document string and added to ChromaDB with metadata (`user_id`, `invoice_id`, `provider`, `model`).
3. **Query** — User question is rewritten to give more context for chroma retrieval and then embedded by ChromaDB's default model, filtered to the user's data, and top-N rows are retrieved.
4. **Reranking** - context is reranked using a cross-encoder from Cohere API
5. **Generate** — Reranked context + chat history are sent to the LLM with a system prompt tailored for FinOps analysis.
6. **Cache** — Chat history is persisted in PostgreSQL per invoice. Optimization results are cached to avoid redundant LLM calls.

---

## Environment Variables

| Variable                        | Description                                    |
|---------------------------------|------------------------------------------------|
| `DATABASE_URL`                  | PostgreSQL connection string                   |
| `KEY`                           | JWT signing secret                             |
| `OPENAI_API_KEY`                | OpenAI / Azure OpenAI API key                  |
| `AZURE_OPENAI_ENDPOINT`         | Azure OpenAI base URL                          |
| `AZURE_OPENAI_DEPLOYMENT_NAME`  | Azure OpenAI model deployment name             |
| `COHERE_API_KEY`                | Cohere API key (for Command R7B)               |

---

## Local Development

### Prerequisites

- Python 3.10+
- PostgreSQL (or use SQLite for quick testing)

### Setup

```bash
# Clone
git clone https://github.com/arjunk08/Gen-AI-Finops-Dashboard.git
cd Gen-AI-Finops-Dashboard

# Virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/finops_db
KEY=your-jwt-secret
OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
COHERE_API_KEY=your-cohere-key
```

### Run

```bash
# Start the FastAPI backend
uvicorn backend.main:app --reload --port 8000

# In a separate terminal, start the Streamlit frontend
streamlit run Dashboard.py
```

> **Note:** When running locally, update `API_BASE_URL` in `Dashboard.py` and the pages to `http://127.0.0.1:8000`.

---

## Testing

Tests use an in-memory SQLite database and FastAPI's `TestClient` — no external services required.

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
DATABASE_URL=sqlite:///./test_dashboard.db pytest tests/ -v
```

### Test Coverage

| Test                          | Endpoint             | Validates                              |
|-------------------------------|----------------------|----------------------------------------|
| `test_read_root`              | `GET /`              | API health check response              |
| `test_register_user`          | `POST /auth/register`| Successful user creation               |
| `test_register_existing_user` | `POST /auth/register`| Duplicate email rejection (400)        |
| `test_login_user_success`     | `POST /auth/login`   | JWT token + user data returned         |
| `test_login_user_invalid_password` | `POST /auth/login` | Wrong password rejection (401)     |
| `test_login_nonexistent_user` | `POST /auth/login`   | Unknown email rejection (401)          |

---

## CI Pipeline

GitHub Actions runs on every push and pull request to `main`:

1. **Ruff Linter** — Static analysis and style checks
2. **Pytest** — Runs the full test suite against a SQLite test database

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for the full workflow.

---

## Deployment

| Component | Platform          | Notes                                                                          |
|-----------|-------------------|--------------------------------------------------------------------------------|
| Backend   | **Render**        | Free tier — may sleep after inactivity (~30s cold start)                       |
| Frontend  | **Streamlit Cloud**| Free tier — may sleep after inactivity                                        |
| Database  | **NeonDB**        | Serverless PostgreSQL — connection string via `DATABASE_URL` environment variable |

---

## Sample Data

The `Sample-data/` directory contains example invoice CSVs compatible with the upload parser:

- `genai_cost_insights_sample_56_rows` — Multi-provider, multi-model cost data
- `sample_anthropic_api_bill_01` — Anthropic API usage details
- `sample_multi_provider_bill_03` — Google Vertex AI usage
- `sample_multi_provider_bill_04` — AWS Bedrock usage

Use these to test the upload, visualization, and AI consultation features.

---

## Demo Account

To explore the live app without registering:

| Field    | Value                  |
|----------|------------------------|
| Email    | `testuser@email.com`   |
| Password | `test123`              |

> The first request after inactivity may take up to 60 seconds while the Render backend wakes up.

---

## Roadmap

- [ ] Forecasting module (time-series models)
- [ ] Enhanced cost optimization with multi-step reasoning
- [ ] Advanced FinOps analytics (budget alerts, anomaly detection)
- [ ] Multi-tenant organization support
- [ ] Expanded LLM provider support

---

## License

Not yet specified.
