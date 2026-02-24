"""
REST API routes for execution/build operations.
Placeholder for Phase 3.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/execution", tags=["execution"])


@router.get("/status")
async def getExecutionStatus():
    """Get current execution status. Phase 3 implementation."""
    return {"status": "not_started", "message": "Execution engine not yet active"}
