from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routes import router  # noqa: E402  (import after load_dotenv)
from db.init_db import init_database  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting MotoMatch RAG MVP...")
    init_database()
    print("[OK] Backend ready!")
    print("     API:  http://localhost:8000")
    print("     Docs: http://localhost:8000/docs")
    print("     Demo: demo@motomatch.local / DemoMotoMatch2024!")
    yield


app = FastAPI(title="MotoMatch RAG MVP", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
