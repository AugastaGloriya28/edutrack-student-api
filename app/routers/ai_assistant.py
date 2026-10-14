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


def _grounded_fallback(question: str, students: List[Student]) -> str:
    """Deterministic, grounded fallback answer engine when Ollama is offline."""
    import re
    q = question.lower()
    total = len(students)

    # 1. Total count
    if any(k in q for k in ["how many student", "total student", "number of student", "count student"]):
        return f"There are currently {total} students registered in the database."

    # 2. Born after / before
    born_after_match = re.search(r"born after (\d{4})", q)
    if born_after_match:
        year = int(born_after_match.group(1))
        matched = [s for s in students if s.date_of_birth.year > year]
        if not matched:
            return f"No students were found born after {year}."
        names = [f"{s.name} (DOB: {s.date_of_birth}, Course: {s.course or 'N/A'})" for s in matched]
        return f"There are {len(matched)} student(s) born after {year}:\n- " + "\n- ".join(names)

    born_before_match = re.search(r"born before (\d{4})", q)
    if born_before_match:
        year = int(born_before_match.group(1))
        matched = [s for s in students if s.date_of_birth.year < year]
        if not matched:
            return f"No students were found born before {year}."
        names = [f"{s.name} (DOB: {s.date_of_birth}, Course: {s.course or 'N/A'})" for s in matched]
        return f"There are {len(matched)} student(s) born before {year}:\n- " + "\n- ".join(names)

    # 3. Youngest / Oldest
    if "youngest" in q:
        youngest = max(students, key=lambda s: s.date_of_birth)
        return f"The youngest student is {youngest.name}, born on {youngest.date_of_birth} (Course: {youngest.course or 'N/A'})."

    if "oldest" in q:
        oldest = min(students, key=lambda s: s.date_of_birth)
        return f"The oldest student is {oldest.name}, born on {oldest.date_of_birth} (Course: {oldest.course or 'N/A'})."

    # 4. Course matching
    courses = {s.course for s in students if s.course}
    for c in courses:
        if c.lower() in q:
            matched = [s for s in students if s.course and s.course.lower() == c.lower()]
            names = [s.name for s in matched]
            return f"There are {len(matched)} student(s) enrolled in {c}: {', '.join(names)}."

    # 5. General summary
    summary_list = [f"{s.name} ({s.course or 'General'}, ID: {s.id})" for s in students[:5]]
    more = f" and {total - 5} more." if total > 5 else "."
    return f"Based on the database records ({total} total students): {', '.join(summary_list)}{more}"


@router.post(
    "/ask",
    response_model=AIQueryResponse,
    summary="Ask the AI assistant a question about students",
    description=(
        "Sends a natural-language question to a locally-running **Ollama** model. "
        "The model only sees data fetched by the backend — it cannot run SQL queries directly. "
        "\n\n**Requires**: Ollama running locally (`ollama serve`) with the `llama3.2:1b` model pulled. "
        "If Ollama is not running, an intelligent grounded fallback engine responds directly."
        "\n\nExample questions:\n"
        "- *How many students are there?*\n"
        "- *List students born after 2005.*\n"
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

    # 2. Call Ollama with grounded fallback if offline
    model_used = OLLAMA_MODEL
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
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
    except Exception:
        # Fallback to local grounded answering from database records
        answer = _grounded_fallback(payload.question, students)
        model_used = f"{OLLAMA_MODEL} (offline fallback: grounded SQLite context)"

    return AIQueryResponse(
        question=payload.question,
        answer=answer,
        model_used=model_used,
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
