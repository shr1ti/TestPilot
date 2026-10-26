
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    expected_result = Column(Text, nullable=False)

    runs = relationship(
        "TestRun",
        back_populates="test_case",
        cascade="all, delete-orphan"
    )


class TestRun(Base):
    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(
        Integer,
        ForeignKey("test_cases.id"),
        nullable=False
    )
    status = Column(String(10), nullable=False)
    notes = Column(Text, nullable=True)

    test_case = relationship(
        "TestCase",
        back_populates="runs"
    )
