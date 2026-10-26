
from pydantic import BaseModel, Field
from typing import Optional, Literal


class TestCaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    expected_result: str = Field(min_length=1)


class TestCaseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    expected_result: str

    model_config = {"from_attributes": True}


class TestRunCreate(BaseModel):
    status: Literal["PASS", "FAIL"]
    notes: Optional[str] = None


class TestRunResponse(BaseModel):
    id: int
    test_case_id: int
    status: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
