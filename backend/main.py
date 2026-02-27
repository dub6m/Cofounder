"""
FastAPI application entry point.
Mounts REST routes, WebSocket endpoint, CORS, and startup hooks.
"""

import json
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes.chat import router as chatRouter
from api.routes.architecture import router as architectureRouter
from api.routes.execution import router as executionRouter
from api.routes.deployment import router as deploymentRouter
from api.websocket.handler import manager
from core.config import settings
from core.database import getSession, initDb
from core.models import Conversation
from schemas.ws_events import EventType
from services.orchestrator.pipeline import handleUserMessage

# ── Logging ────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-30s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cofounder")


# ── Lifespan ───────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    logger.info("🚀 Cofounder backend starting...")
    await initDb()
    logger.info("✅ Database tables verified")
    yield
    logger.info("👋 Cofounder backend shutting down")


# ── App ────────────────────────────────────────────────────────

app = FastAPI(
    title="Cofounder API",
    description="AI Codebase Orchestrator — Design-First, Code-Second",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST Routes ────────────────────────────────────────────────

app.include_router(chatRouter)
app.include_router(architectureRouter)
app.include_router(executionRouter)
app.include_router(deploymentRouter)


@app.get("/")
async def root():
    return {
        "name": "Cofounder API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def healthCheck():
    return {"status": "healthy"}


# ── WebSocket Endpoint ─────────────────────────────────────────

@app.websocket("/ws")
async def websocketEndpoint(websocket: WebSocket):
    import uuid as _uuid
    clientId = str(_uuid.uuid4())[:8]
    await manager.connect(websocket, clientId)

    try:
        while True:
            rawData = await websocket.receive_text()

            try:
                data = json.loads(rawData)
            except json.JSONDecodeError:
                await manager.sendEvent(
                    EventType.ERROR,
                    {"message": "Invalid JSON"},
                    clientId=clientId,
                )
                continue

            eventType = data.get("event_type", "")
            payload = data.get("payload", {})

            # ── Handle user_message ────────────────────────
            if eventType == "user_message":
                content = payload.get("content", "").strip()
                if not content:
                    continue

                conversationId = payload.get("conversation_id")

                # Get or create DB session
                async for session in getSession():
                    try:
                        # Get or create conversation
                        if conversationId:
                            conversation = await session.get(
                                Conversation, conversationId
                            )
                        else:
                            conversation = None

                        if not conversation:
                            conversation = Conversation(
                                title=content[:100]
                            )
                            session.add(conversation)
                            await session.flush()
                            conversationId = conversation.id

                            # Notify the frontend of the new conversation ID
                            await manager.sendEvent(
                                EventType.PHASE_CHANGE,
                                {
                                    "from_phase": "init",
                                    "to_phase": "negotiation",
                                    "conversation_id": conversationId,
                                },
                                clientId=clientId,
                            )

                        await handleUserMessage(
                            session, conversationId, content, clientId
                        )
                    except Exception as e:
                        logger.error(f"Error handling message: {e}", exc_info=True)
                        await manager.sendEvent(
                            EventType.ERROR,
                            {"message": f"Internal error: {str(e)}"},
                            clientId=clientId,
                        )


    except WebSocketDisconnect:
        manager.disconnect(clientId)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(clientId)
