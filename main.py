
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import TestCase, TestRun
from schemas import (
    TestCaseCreate,
    TestCaseResponse,
    TestRunCreate,
    TestRunResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Mini QA Test Manager",
    lifespan=lifespan,
)


@app.post(
    "/test-cases",
    response_model=TestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_case(
    data: TestCaseCreate,
    db: Session = Depends(get_db),
):
    test_case = TestCase(**data.model_dump())
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


@app.get("/test-cases", response_model=list[TestCaseResponse])
def list_test_cases(db: Session = Depends(get_db)):
    return db.query(TestCase).order_by(TestCase.id).all()


@app.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
):
    test_case = db.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    return test_case


@app.patch("/test-cases/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(
    test_case_id: int,
    data: TestCaseCreate,
    db: Session = Depends(get_db),
):
    test_case = db.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    for key, value in data.model_dump().items():
        setattr(test_case, key, value)

    db.commit()
    db.refresh(test_case)
    return test_case


@app.delete("/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
):
    test_case = db.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    db.delete(test_case)
    db.commit()


@app.post(
    "/test-cases/{test_case_id}/runs",
    response_model=TestRunResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_run(
    test_case_id: int,
    data: TestRunCreate,
    db: Session = Depends(get_db),
):
    test_case = db.get(TestCase, test_case_id)

    if test_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    test_run = TestRun(
        test_case_id=test_case_id,
        **data.model_dump(),
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    return test_run


@app.get(
    "/test-cases/{test_case_id}/runs",
    response_model=list[TestRunResponse],
)
def list_test_runs(
    test_case_id: int,
    db: Session = Depends(get_db),
):
    if db.get(TestCase, test_case_id) is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    return (
        db.query(TestRun)
        .filter(TestRun.test_case_id == test_case_id)
        .order_by(TestRun.id)
        .all()
    )
