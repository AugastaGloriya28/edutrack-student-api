"""
SQLAlchemy ORM model for the Student table.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(180), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    course = Column(String(120), nullable=True)
    address = Column(String(300), nullable=True)
    enrollment_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
