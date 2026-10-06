# MotoMatch RAG MVP

Local RAG (Retrieval-Augmented Generation) system for motorcycle parts
compatibility. Ask a natural-language question, get an answer grounded in a
parts catalog, with its sources and a confidence score — plus a full
observability stack so you can see exactly what the system is doing.

## Architecture

```
┌──────────────┐     ┌─────────────────────────────────────────────┐
│  React/Vite  │────▶│  FastAPI backend (:8000)                    │
│   (:5173)    │     │                                             │
└──────────────┘     │  query ──▶ local embeddings (MiniLM)        │
                     │        ──▶ vector search (LanceDB)          │
                     │        ──▶ GPT-4o-mini (OpenAI)             │
                     │        ──▶ answer + sources + confidence    │
                     │                                             │
                     │  /metrics ◀── scraped by Prometheus         │
                     └─────────────────────────────────────────────┘
                                         │
                            ┌────────────┴────────────┐
                            ▼                          ▼
                     Prometheus (:9090)  ──────▶  Grafana (:3000)
```

| Layer       | Tech                                   | Notes                     |
| ----------- | -------------------------------------- | ------------------------- |
| Frontend    | React 18 + Vite 5                      | —                         |
| Backend     | FastAPI + Uvicorn                      | —                         |
| Embeddings  | `sentence-transformers` (all-MiniLM)   | Local, no API key         |
| Vector DB   | LanceDB                                | Local, file-based         |
| LLM         | OpenAI `gpt-4o-mini`                   | JSON mode                 |
| Relational  | SQLite                                 | Users, documents, logs    |
| Monitoring  | Prometheus + Grafana                   | Docker                    |

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (with npm)
- **An OpenAI API key** — https://platform.openai.com/api-keys
- **Docker Desktop** — only for the monitoring stack (optional)

> **Windows / PowerShell note:** PowerShell does **not** accept `&&` to chain
> commands. Run the commands one per line (as shown below). The examples use
> the venv's Python directly (`.\venv\Scripts\python.exe`) to avoid
> execution-policy issues with `Activate.ps1`.

---

## 1. Backend

From the repo root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Add your OpenAI API key

Create a file named **`.env`** inside `backend/` (same folder as `main.py`):

```
OPENAI_API_KEY=sk-proj-your-real-key-here
JWT_SECRET=motomatch-demo-secret-key-2024
```

> The key is only needed for the `/query` endpoint. Login and startup work
> without it. `.env` is git-ignored and never leaves your machine.

### Run the backend

```powershell
.\venv\Scripts\python.exe main.py
```

First start takes ~30–60s (downloads the embedding model and seeds the DB with
10 sample catalog docs). When you see `[OK] Backend ready!` it's up.

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

### Backend dependencies (`backend/requirements.txt`)

`fastapi`, `uvicorn[standard]`, `sqlalchemy`, `openai`, `lancedb`,
`sentence-transformers`, `python-dotenv`, `python-multipart`, `pydantic`,
`PyJWT`, `prometheus-fastapi-instrumentator`.

---

## 2. Frontend

In a **second terminal**, from the repo root:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Demo credentials (pre-filled on the login screen)

- Email: `demo@motomatch.local`
- Password: `DemoMotoMatch2024!`

### Try it

> Is the Honda CB650F alternator compatible with the CBR650R?

Expected: **No** — the CB650F uses a 3-pin (mechanical) regulator and the
CBR650R uses a 4-pin (electronic) one.

### Frontend dependencies (`frontend/package.json`)

`react`, `react-dom`, `react-router-dom`, `axios` (+ `vite` and
`@vitejs/plugin-react` for dev/build).

---

## 3. Monitoring (optional — needs Docker)

The backend exposes Prometheus metrics at `/metrics`. The stack in
`monitoring/` scrapes them and renders a ready-made Grafana dashboard.

```powershell
cd monitoring
docker compose up -d
```

- **Grafana:** http://localhost:3000 — dashboard **"MotoMatch RAG
  Observability"** loads automatically (anonymous admin access for local use).
- **Prometheus:** http://localhost:9090

What the dashboard shows: total queries, errors, average answer confidence,
query rate, HTTP request rate per endpoint, and **latency split by stage**
(end-to-end vs vector retrieval vs the OpenAI call) so you can see where the
time actually goes.

Stop it with:

```powershell
docker compose down
```

> The backend runs on your host, not in Docker. Prometheus reaches it via
> `host.docker.internal:8000`. If you (re)start the backend, the dashboard
> picks it back up within a few seconds.

### Custom metrics exposed

| Metric                            | Type      | Meaning                        |
| --------------------------------- | --------- | ------------------------------ |
| `rag_queries_total`               | counter   | Queries processed              |
| `rag_query_errors_total`          | counter   | Queries that errored           |
| `rag_query_duration_seconds`      | histogram | End-to-end latency             |
| `rag_retrieval_duration_seconds`  | histogram | Vector retrieval latency       |
| `rag_llm_duration_seconds`        | histogram | OpenAI call latency            |
| `rag_answer_confidence`           | histogram | Model-reported confidence      |

---

## Troubleshooting

- **`The token '&&' is not a valid statement separator`** — you're in
  PowerShell. Run commands one per line instead of chaining with `&&`.
- **Login says "Invalid credentials" but the password is correct** — usually
  the backend isn't running or isn't reachable. Check http://localhost:8000/health.
- **OpenAI errors on `/query`** — check `OPENAI_API_KEY` in `backend/.env` and
  your quota at https://platform.openai.com.
- **Reset the database** — delete `backend/data/motomatch.db` and
  `backend/data/vectors/`, then restart the backend to re-seed.
