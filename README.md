# MotoMatch RAG MVP

Local RAG system for motorcycle parts compatibility, using OpenAI for generation
and local embeddings for retrieval.

## Stack

1. **Embeddings**: `sentence-transformers` (local, no API key)
2. **Vector DB**: LanceDB (local, file-based)
3. **LLM**: OpenAI `gpt-4o-mini` (JSON mode)
4. **DB**: SQLite (local)
5. **Frontend**: React + Vite

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 2. Add your OpenAI API key

Create a file named `.env` inside `backend/` with this content:

```
OPENAI_API_KEY=sk-proj-your-real-key-here
JWT_SECRET=motomatch-demo-secret-key-2024
```

Get a key at https://platform.openai.com/api-keys

### 3. Start the backend

```bash
python main.py
# API on http://localhost:8000  (docs at /docs)
```

On first start it auto-creates the DB, seeds 10 sample part catalog docs, and
builds their embeddings (~30-60s the first time while the embedding model
downloads).

### 4. Frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
# App on http://localhost:5173
```

## Demo Credentials

- Email: `demo@motomatch.local`
- Password: `DemoMotoMatch2024!`

(Both are pre-filled on the login screen.)

## Try it

Login, then ask something like:

> Is the CB650F 2018 alternator compatible with the 2020?

You get a RAG answer with its sources and a confidence score.

## Notes / Fixes vs. the original spec

- Dependencies use modern, compatible versions to avoid the classic
  `sentence-transformers==2.2.2` / `huggingface_hub` install failure.
- All paths are anchored to the `backend/` directory (via `config.py`), so it
  runs the same from the repo root or from inside `backend/`.
- OpenAI calls use JSON mode for reliable parsing.
- `startup` event replaced with the modern FastAPI `lifespan` handler.
- Query logs record the real authenticated user id; analytics counts real queries.

## Troubleshooting

**Reset the database:** delete `backend/data/motomatch.db` and
`backend/data/vectors/`, then restart the backend to re-seed.

**OpenAI errors:** check `OPENAI_API_KEY` in `backend/.env` and your quota at
https://platform.openai.com
