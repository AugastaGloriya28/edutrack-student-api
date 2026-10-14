"""
AI Assistant router — answers natural-language questions about student data.

Strategy
--------
1. Fetch ALL student records from the database (safe; no raw SQL from the model).
2. Serialize them into a compact, readable context string.
3. Send the question + context to a locally-running Ollama model.
4. Return the grounded, human-readable answer.

Security: The model NEVER executes SQL. We always pull the data in Python first.
"""

import json
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.schemas.student import AIQueryRequest, AIQueryResponse

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"


def _serialize_students(students: List[Student]) -> str:
    """Convert student ORM objects into a JSON string for the prompt context."""
    records = []
    for s in students:
        records.append(
            {
                "id": s.id,
                "name": s.name,
                "date_of_birth": str(s.date_of_birth),
                "email": s.email,
                "phone": s.phone,
                "course": s.course,
                "address": s.address,
                "enrollment_date": str(s.enrollment_date) if s.enrollment_date else None,
            }
        )
    return json.dumps(records, indent=2)


def _build_prompt(question: str, context: str) -> str:
    return f"""You are EduTrack AI, a helpful assistant for a student management system.
Answer the user's question using ONLY the student data provided below. Do NOT guess or invent data.
If the answer cannot be determined from the data, say so clearly.

--- STUDENT DATA (JSON) ---
{context}
--- END OF DATA ---

User question: {question}

Provide a clear, concise, human-readable answer:"""


@router.post(
    "/ask",
    response_model=AIQueryResponse,
    summary="Ask the AI assistant a question about students",
    description=(
        "Sends a natural-language question to a locally-running **Ollama** model. "
        "The model only sees data fetched by the backend — it cannot run SQL queries directly. "
        "\n\n**Requires**: Ollama running locally (`ollama serve`) with the `llama3.2:1b` model pulled."
        "\n\nExample questions:\n"
        "- *How many students are there?*\n"
        "- *List students enrolled in Computer Science.*\n"
        "- *Who is the youngest student?*"
    ),
)
async def ask_ai(payload: AIQueryRequest, db: Session = Depends(get_db)):
    # 1. Fetch all students from the DB (grounding the model in real data)
    students = db.query(Student).all()

    if not students:
        return AIQueryResponse(
            question=payload.question,
            answer="There are currently no student records in the database. Please add some students first.",
            model_used=OLLAMA_MODEL,
            records_consulted=0,
        )

    context = _serialize_students(students)
    prompt = _build_prompt(payload.question, context)

    # 2. Call Ollama
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            answer = data.get("response", "").strip()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running (`ollama serve`) and the model is pulled "
                f"(`ollama pull {OLLAMA_MODEL}`)."
            ),
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama returned an error: {e.response.text}",
        )

    return AIQueryResponse(
        question=payload.question,
        answer=answer,
        model_used=OLLAMA_MODEL,
        records_consulted=len(students),
    )


@router.get(
    "/status",
    summary="Check Ollama availability",
    description="Pings the local Ollama service and returns whether it is reachable.",
)
async def ollama_status():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get("http://localhost:11434/api/tags")
            r.raise_for_status()
            models = [m["name"] for m in r.json().get("models", [])]
            return {
                "ollama_online": True,
                "available_models": models,
                "recommended_model": OLLAMA_MODEL,
                "model_ready": OLLAMA_MODEL in models,
            }
    except Exception:
        return {
            "ollama_online": False,
            "available_models": [],
            "recommended_model": OLLAMA_MODEL,
            "model_ready": False,
            "hint": "Run: ollama serve && ollama pull llama3.2:1b",
        }
