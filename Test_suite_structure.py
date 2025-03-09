# Pydantic
from pydantic import BaseModel
from typing import List, Union

class Step(BaseModel):
    action: str
    field: str | None = None
    element: str | None = None
    value: str | None = None

class ExpectedResult(BaseModel):
    type: str
    url: str

class TestCase(BaseModel):
    title: str
    preconditions: str
    steps: List[Step]
    expectedResults: ExpectedResult
    edgeCases: List[str]

class TestSuite(BaseModel):
    testCases: List[TestCase]
    pomCode: str

