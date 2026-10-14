"""
CRUD router for student records.

Routes
------
POST   /students/              — Create a student
GET    /students/              — List / filter students
GET    /students/{student_id}  — Get a single student
PUT    /students/{student_id}  — Replace a student's details
PATCH  /students/{student_id}  — Partially update a student
DELETE /students/{student_id}  — Remove a student
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter()


# ── helpers ────────────────────────────────────────────────────────────────────

def _get_or_404(student_id: int, db: Session) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id={student_id} not found.",
        )
    return student


# ── Create ─────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description=(
        "Registers a new student in the database. "
        "Email must be unique. All mandatory fields must be provided."
    ),
)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    # Duplicate email guard
    existing = db.query(Student).filter(Student.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A student with email '{payload.email}' already exists.",
        )

    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


# ── Read (list) ────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[StudentResponse],
    summary="List all students",
    description="Returns a paginated list of students. Supports filtering by name, course, and date-of-birth range.",
)
def list_students(
    name: Optional[str] = Query(None, description="Filter by partial name (case-insensitive)"),
    course: Optional[str] = Query(None, description="Filter by partial course name (case-insensitive)"),
    dob_after: Optional[date] = Query(None, description="Include students born after this date (YYYY-MM-DD)"),
    dob_before: Optional[date] = Query(None, description="Include students born before this date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return (1-100)"),
    db: Session = Depends(get_db),
):
    q = db.query(Student)

    if name:
        q = q.filter(Student.name.ilike(f"%{name}%"))
    if course:
        q = q.filter(Student.course.ilike(f"%{course}%"))
    if dob_after:
        q = q.filter(Student.date_of_birth > dob_after)
    if dob_before:
        q = q.filter(Student.date_of_birth < dob_before)

    return q.order_by(Student.id).offset(skip).limit(limit).all()


# ── Read (single) ──────────────────────────────────────────────────────────────

@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get a student by ID",
    description="Retrieves a single student record by their unique numeric ID.",
)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return _get_or_404(student_id, db)


# ── Update (full replace) ──────────────────────────────────────────────────────

@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Replace a student record (full update)",
    description="Replaces all editable fields of a student record.",
)
def replace_student(
    student_id: int,
    payload: StudentCreate,
    db: Session = Depends(get_db),
):
    student = _get_or_404(student_id, db)

    # Allow email update only if it belongs to this student or doesn't exist
    conflict = (
        db.query(Student)
        .filter(Student.email == payload.email, Student.id != student_id)
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' is already used by another student.",
        )

    for field, value in payload.model_dump().items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


# ── Update (partial) ───────────────────────────────────────────────────────────

@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Partially update a student record",
    description="Updates only the supplied fields of a student record.",
)
def patch_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
):
    student = _get_or_404(student_id, db)

    updates = payload.model_dump(exclude_unset=True)

    # Unique-email guard
    if "email" in updates:
        conflict = (
            db.query(Student)
            .filter(Student.email == updates["email"], Student.id != student_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{updates['email']}' is already used by another student.",
            )

    for field, value in updates.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


# ── Delete ─────────────────────────────────────────────────────────────────────

@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student",
    description="Permanently removes a student record from the database.",
)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = _get_or_404(student_id, db)
    db.delete(student)
    db.commit()
