"""
Pydantic schema for SCOUT_REPORT.json validation.
Enforced via LLM system prompt and validated on receipt.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TestFailure(BaseModel):
    testName: str = Field(..., alias="test_name")
    errorMessage: str = Field(..., alias="error_message")

    class Config:
        populate_by_name = True


class ScoutReport(BaseModel):
    frictionDetected: bool = Field(..., alias="friction_detected")
    severity: str = Field(..., description="'low' or 'blocker'")
    issueDescription: str = Field(..., alias="issue_description")
    suggestedArchitecture: Optional[str] = Field(
        None, alias="suggested_architecture"
    )
    failingNode: Optional[str] = Field(None, alias="failing_node")
    testFailures: Optional[list[TestFailure]] = Field(
        None, alias="test_failures"
    )

    class Config:
        populate_by_name = True
