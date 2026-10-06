import json
import os
import time

from openai import OpenAI
from sqlalchemy.orm import Session

from db.models import QueryLog
from metrics import (
    RAG_CONFIDENCE,
    RAG_ERRORS,
    RAG_LATENCY,
    RAG_LLM_LATENCY,
    RAG_QUERIES,
    RAG_RETRIEVAL_LATENCY,
)
from rag.retriever import Retriever

SYSTEM_PROMPT = """You are an expert motorcycle parts compatibility assistant.
Given a user question and relevant documentation, provide accurate answers about \
part compatibility.
Respond ONLY with a JSON object of the form:
{"answer": "...", "confidence": 0.0-1.0, "reasoning": "..."}"""


class RagPipeline:
    def __init__(self, db_session: Session):
        self.retriever = Retriever(db_session)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.db_session = db_session

    def query(self, question: str, user_id: int = 1) -> dict:
        start_time = time.time()
        RAG_QUERIES.inc()

        try:
            # 1. Retrieve context (timed separately)
            retrieval_start = time.time()
            context = self.retriever.retrieve_context(question, top_k=5)
            RAG_RETRIEVAL_LATENCY.observe(time.time() - retrieval_start)

            # 2. Build prompt
            context_text = "\n\n".join(
                f"Source: {c['source_doc']}\n{c['chunk_text']}" for c in context
            )
            user_prompt = (
                f"Question: {question}\n\n"
                f"Relevant documentation:\n{context_text}\n\n"
                "Please answer the question based on the documentation provided."
            )

            # 3. Call OpenAI API (timed separately; JSON mode for safe parsing)
            llm_start = time.time()
            message = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=500,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            RAG_LLM_LATENCY.observe(time.time() - llm_start)
            response_text = message.choices[0].message.content

            try:
                response_data = json.loads(response_text)
            except (json.JSONDecodeError, TypeError):
                response_data = {
                    "answer": response_text or "",
                    "confidence": 0.7,
                    "reasoning": "Direct response from OpenAI",
                }
        except Exception:
            RAG_ERRORS.inc()
            raise

        response_time_ms = int((time.time() - start_time) * 1000)
        RAG_LATENCY.observe(time.time() - start_time)

        confidence = response_data.get("confidence", 0) or 0
        try:
            RAG_CONFIDENCE.observe(float(confidence))
        except (TypeError, ValueError):
            pass

        # 4. Log query
        query_log = QueryLog(
            user_id=user_id,
            question=question,
            answer=response_data.get("answer", ""),
            confidence=confidence,
            response_time_ms=response_time_ms,
        )
        self.db_session.add(query_log)
        self.db_session.commit()

        return {
            "answer": response_data.get("answer", ""),
            "confidence": confidence,
            "reasoning": response_data.get("reasoning", ""),
            "sources": context,
            "response_time_ms": response_time_ms,
        }
