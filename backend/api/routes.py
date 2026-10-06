from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from api.schemas import QueryRequest
from auth.jwt_handler import create_access_token, verify_token
from auth.schemas import LoginRequest, TokenResponse
from config import DEMO_EMAIL, DEMO_PASSWORD
from db.init_db import SessionLocal
from db.models import Document, QueryLog, User
from rag.rag_pipeline import RagPipeline

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Auth endpoints
@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    if request.email == DEMO_EMAIL and request.password == DEMO_PASSWORD:
        token = create_access_token(request.email)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")


# Protected endpoints
@router.get("/documents")
def list_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    docs = db.query(Document).all()
    return [
        {"id": d.id, "title": d.title, "uploaded_at": d.uploaded_at} for d in docs
    ]


@router.post("/query")
def rag_query(
    request: QueryRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    pipeline = RagPipeline(db)
    return pipeline.query(request.question, user_id=current_user.id)


@router.get("/analytics")
def analytics(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {
        "total_documents": db.query(Document).count(),
        "total_queries": db.query(QueryLog).count(),
    }
