"""Central path and configuration resolution.

All filesystem paths are anchored to this file's location, so the backend
behaves identically whether you run `python main.py` from the repo root or
from inside the `backend/` directory. No more `backend/backend/...` surprises.
"""
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
SEED_DOCS_DIR = DATA_DIR / "seed_docs"
VECTORS_DIR = DATA_DIR / "vectors"
DB_PATH = DATA_DIR / "motomatch.db"

# Ensure the data directory exists before anything tries to write to it.
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")
JWT_SECRET = os.getenv("JWT_SECRET", "motomatch-demo-secret-key-2024")

# Demo credentials (local demo only — not a real auth system).
DEMO_EMAIL = "demo@motomatch.local"
DEMO_PASSWORD = "DemoMotoMatch2024!"
