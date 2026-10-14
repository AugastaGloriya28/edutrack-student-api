"""
Pydantic schemas for request / response validation.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


# ── Helpers ────────────────────────────────────────────────────────────────────

PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


# ── Create ─────────────────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    """Payload to create a new student record."""

    name: str
    date_of_birth: date
    email: EmailStr
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name must not be empty.")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and not PHONE_RE.match(v):
                raise ValueError("Phone number format is invalid.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("Date of birth must be in the past.")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Priya Sharma",
                "date_of_birth": "2003-07-15",
                "email": "priya.sharma@example.com",
                "phone": "+91 98765 43210",
                "course": "B.Tech Computer Science",
                "address": "12, Rose Garden, Bengaluru, Karnataka",
                "enrollment_date": "2022-08-01",
            }
        }
    )


# ── Update (all fields optional for PATCH semantics) ───────────────────────────

class StudentUpdate(BaseModel):
    """Payload to partially update an existing student record."""

    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Name must not be empty.")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if v and not PHONE_RE.match(v):
                raise ValueError("Phone number format is invalid.")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "course": "M.Tech Data Science",
                "phone": "+91 99887 76655",
            }
        }
    )


# ── Response ───────────────────────────────────────────────────────────────────

class StudentResponse(BaseModel):
    """Student record returned by the API."""

    id: int
    name: str
    date_of_birth: date
    email: str
    phone: Optional[str]
    course: Optional[str]
    address: Optional[str]
    enrollment_date: Optional[date]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ── AI Query ───────────────────────────────────────────────────────────────────

class AIQueryRequest(BaseModel):
    """Natural-language question for the AI assistant."""

    question: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question": "How many students are enrolled in B.Tech Computer Science?"
            }
        }
    )


class AIQueryResponse(BaseModel):
    """Response from the AI assistant."""

    question: str
    answer: str
    model_used: str
    records_consulted: int
