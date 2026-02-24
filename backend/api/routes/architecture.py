"""
REST API routes for architecture diagram operations.
Placeholder for Phase 2 — endpoints will serve diagram data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import getSession
from core.models import ArchitectureSnapshot

router = APIRouter(prefix="/api/architecture", tags=["architecture"])


@router.get("/{conversationId}/latest")
async def getLatestSnapshot(
    conversationId: str,
    session: AsyncSession = Depends(getSession),
):
    """Get the latest architecture snapshot for a conversation."""
    result = await session.execute(
        select(ArchitectureSnapshot)
        .where(ArchitectureSnapshot.conversationId == conversationId)
        .order_by(ArchitectureSnapshot.version.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No architecture snapshots found")

    return {
        "id": snapshot.id,
        "conversation_id": snapshot.conversationId,
        "version": snapshot.version,
        "flowchart": snapshot.flowchart,
        "erd": snapshot.erd,
        "sequence": snapshot.sequence,
        "is_finalized": snapshot.isFinalized,
        "created_at": snapshot.createdAt.isoformat(),
    }


@router.get("/{conversationId}/history")
async def getSnapshotHistory(
    conversationId: str,
    session: AsyncSession = Depends(getSession),
):
    """Get all architecture snapshot versions for a conversation."""
    result = await session.execute(
        select(ArchitectureSnapshot)
        .where(ArchitectureSnapshot.conversationId == conversationId)
        .order_by(ArchitectureSnapshot.version.asc())
    )
    snapshots = result.scalars().all()

    return [
        {
            "id": s.id,
            "version": s.version,
            "is_finalized": s.isFinalized,
            "created_at": s.createdAt.isoformat(),
        }
        for s in snapshots
    ]
