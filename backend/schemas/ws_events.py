"""
Pydantic models for WebSocket event envelope and all event payloads.
Strictly enforces the event dictionary from IMPLEMENTATION_PLAN.md.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EventType(str, Enum):
    CHAT_MESSAGE = "chat_message"
    DECISION_REQUIRED = "decision_required"
    DECISION_RESPONSE = "decision_response"
    GRAPH_UPDATE = "graph_update"
    EXECUTION_PROGRESS = "execution_progress"
    TEST_RESULT = "test_result"
    SCOUT_ALERT = "scout_alert"
    DEPLOYMENT_SUCCESS = "deployment_success"
    USER_MESSAGE = "user_message"
    PHASE_CHANGE = "phase_change"
    ERROR = "error"


class WsEnvelope(BaseModel):
    """Strict event envelope: all WS messages must conform to this shape."""
    eventType: EventType = Field(..., alias="event_type")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    payload: dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


# ── Event Payloads ──────────────────────────────────────────────


class ChatMessagePayload(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    metadata: Optional[dict[str, Any]] = None


class DecisionOption(BaseModel):
    label: str
    value: str
    description: str = ""


class DecisionRequiredPayload(BaseModel):
    id: str
    question: str
    options: list[DecisionOption]


class DecisionResponsePayload(BaseModel):
    decisionId: str = Field(..., alias="decision_id")
    selectedValue: str = Field(..., alias="selected_value")

    class Config:
        populate_by_name = True


class GraphUpdatePayload(BaseModel):
    diagramType: str = Field(..., alias="diagram_type")  # 'flowchart' | 'erd' | 'sequence'
    mermaidSource: str = Field(..., alias="mermaid_source")
    diff: Optional[str] = None

    class Config:
        populate_by_name = True


class ExecutionProgressPayload(BaseModel):
    stepIndex: int = Field(..., alias="step_index")
    stepLabel: str = Field(..., alias="step_label")
    status: str  # 'pending' | 'running' | 'passed' | 'failed'

    class Config:
        populate_by_name = True


class TestResultPayload(BaseModel):
    exitCode: int = Field(..., alias="exit_code")
    summary: str
    stderrTail: Optional[str] = Field(None, alias="stderr_tail")

    class Config:
        populate_by_name = True


class ScoutAlertPayload(BaseModel):
    severity: str  # 'low' | 'blocker'
    issueDescription: str = Field(..., alias="issue_description")
    suggestedArchitecture: Optional[str] = Field(None, alias="suggested_architecture")

    class Config:
        populate_by_name = True


class DeploymentSuccessPayload(BaseModel):
    repoUrl: str = Field(..., alias="repo_url")
    commitHash: str = Field(..., alias="commit_hash")
    branch: str

    class Config:
        populate_by_name = True


class UserMessagePayload(BaseModel):
    content: str


class PhaseChangePayload(BaseModel):
    fromPhase: str = Field(..., alias="from_phase")
    toPhase: str = Field(..., alias="to_phase")

    class Config:
        populate_by_name = True
