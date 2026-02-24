"""
REST API routes for GitHub deployment operations.
Placeholder for Phase 4.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/deployment", tags=["deployment"])


@router.get("/status")
async def getDeploymentStatus():
    """Get current deployment status. Phase 4 implementation."""
    return {"status": "not_started", "message": "Deployment engine not yet active"}
