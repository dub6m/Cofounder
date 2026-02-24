"""
Docker Sandbox Manager — runs Aider-generated code inside ephemeral containers
with live WebSocket log streaming.

Key design decisions:
  - Containers run `detach=True` so the backend never blocks.
  - Logs are streamed via `container.logs(stream=True)` and forwarded
    to the frontend through WebSocket `execution_progress` / `test_result` events.
  - Containers are force-killed after `settings.sandbox_timeout` seconds.
  - Each execution gets a unique container name to avoid collisions.
"""

import asyncio
import logging
import uuid
from typing import Optional

import docker
from docker.errors import DockerException, NotFound, ImageNotFound

from core.config import settings
from api.websocket.handler import manager
from schemas.ws_events import EventType

logger = logging.getLogger(__name__)


class DockerManager:
    """Manages ephemeral Docker sandbox containers for code execution."""

    def __init__(self):
        self._client: Optional[docker.DockerClient] = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            try:
                self._client = docker.from_env()
                self._client.ping()
                logger.info("Docker daemon connected")
            except DockerException as e:
                logger.error(f"Docker daemon not available: {e}")
                raise RuntimeError(
                    "Docker Desktop is not running. "
                    "Start Docker Desktop and try again."
                ) from e
        return self._client

    def isAvailable(self) -> bool:
        """Check if Docker daemon is reachable."""
        try:
            _ = self.client
            return True
        except RuntimeError:
            return False

    async def runSandbox(
        self,
        conversationId: str,
        workspacePath: str,
        clientId: str = "default",
        command: Optional[str] = None,
    ) -> dict:
        """
        Launch a sandbox container in detach mode and stream logs live.

        Args:
            conversationId: Links this execution to a UI conversation.
            workspacePath: Host directory to mount into /workspace.
            clientId: WebSocket client to stream events to.
            command: Optional override command (default: pytest from Dockerfile).

        Returns:
            dict with exit_code, logs summary, and container_id.
        """
        containerName = f"cofounder-sandbox-{uuid.uuid4().hex[:8]}"

        # Notify frontend: execution starting
        await manager.sendEvent(
            EventType.EXECUTION_PROGRESS,
            {
                "step_index": 0,
                "step_label": "Launching sandbox...",
                "status": "running",
            },
            clientId=clientId,
        )

        try:
            # Pull image if not present
            try:
                self.client.images.get(settings.sandbox_image)
            except ImageNotFound:
                logger.info(f"Pulling sandbox image: {settings.sandbox_image}")
                await manager.sendEvent(
                    EventType.EXECUTION_PROGRESS,
                    {
                        "step_index": 0,
                        "step_label": "Pulling sandbox image...",
                        "status": "running",
                    },
                    clientId=clientId,
                )
                self.client.images.pull(settings.sandbox_image)

            # Create and start container (detached)
            containerArgs = {
                "image": settings.sandbox_image,
                "name": containerName,
                "detach": True,
                "volumes": {
                    workspacePath: {
                        "bind": settings.sandbox_workspace,
                        "mode": "rw",
                    }
                },
                "working_dir": settings.sandbox_workspace,
                "mem_limit": "512m",
                "cpu_quota": 50000,  # 50% of one core
                "network_mode": "none",  # security: no network access
            }
            if command:
                containerArgs["command"] = command

            container = self.client.containers.run(**containerArgs)

            logger.info(
                f"Sandbox container started: {containerName} "
                f"(conversation: {conversationId})"
            )

            # Notify frontend: container running
            await manager.sendEvent(
                EventType.EXECUTION_PROGRESS,
                {
                    "step_index": 1,
                    "step_label": "Running tests...",
                    "status": "running",
                },
                clientId=clientId,
            )

            # Stream logs live to frontend
            allLogs = await self._streamLogs(
                container, clientId, conversationId
            )

            # Wait for container exit (with timeout)
            exitResult = await asyncio.wait_for(
                asyncio.to_thread(container.wait),
                timeout=settings.sandbox_timeout,
            )
            exitCode = exitResult.get("StatusCode", -1)

        except asyncio.TimeoutError:
            logger.warning(
                f"Sandbox timed out after {settings.sandbox_timeout}s: "
                f"{containerName}"
            )
            try:
                container.kill()
            except Exception:
                pass
            exitCode = -1
            allLogs = "[TIMEOUT] Container exceeded time limit."

        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            exitCode = -1
            allLogs = f"[ERROR] {str(e)}"

        finally:
            # Cleanup: remove container
            try:
                c = self.client.containers.get(containerName)
                c.remove(force=True)
                logger.info(f"Sandbox container removed: {containerName}")
            except (NotFound, Exception):
                pass

        # Determine pass/fail
        status = "passed" if exitCode == 0 else "failed"

        # Notify frontend: test result
        await manager.sendEvent(
            EventType.EXECUTION_PROGRESS,
            {
                "step_index": 2,
                "step_label": "Tests complete",
                "status": status,
            },
            clientId=clientId,
        )

        stderrTail = allLogs[-2000:] if len(allLogs) > 2000 else allLogs

        await manager.sendEvent(
            EventType.TEST_RESULT,
            {
                "exit_code": exitCode,
                "summary": f"{'✅ All tests passed' if exitCode == 0 else '❌ Tests failed'}",
                "stderr_tail": stderrTail,
            },
            clientId=clientId,
        )

        return {
            "exit_code": exitCode,
            "logs": allLogs,
            "container_id": containerName,
        }

    async def _streamLogs(
        self,
        container,
        clientId: str,
        conversationId: str,
    ) -> str:
        """
        Read container logs as a live stream and forward chunks to
        the frontend via WebSocket. Non-blocking via asyncio.to_thread.

        Returns the full concatenated log output.
        """
        allLines: list[str] = []

        def _readStream():
            """Blocking generator — runs in a thread."""
            for chunk in container.logs(stream=True, follow=True):
                line = chunk.decode("utf-8", errors="replace")
                allLines.append(line)

        # Stream in a background thread so we don't block the event loop
        streamTask = asyncio.create_task(asyncio.to_thread(_readStream))

        # While the stream is running, periodically flush to the frontend
        lastSent = 0
        while not streamTask.done():
            await asyncio.sleep(0.5)  # flush every 500ms
            if len(allLines) > lastSent:
                batch = "".join(allLines[lastSent:])
                lastSent = len(allLines)
                await manager.sendEvent(
                    EventType.EXECUTION_PROGRESS,
                    {
                        "step_index": 1,
                        "step_label": "Running tests...",
                        "status": "running",
                        "log_chunk": batch,
                    },
                    clientId=clientId,
                )

        # Flush any remaining lines
        await streamTask
        if len(allLines) > lastSent:
            batch = "".join(allLines[lastSent:])
            await manager.sendEvent(
                EventType.EXECUTION_PROGRESS,
                {
                    "step_index": 1,
                    "step_label": "Running tests...",
                    "status": "running",
                    "log_chunk": batch,
                },
                clientId=clientId,
            )

        return "".join(allLines)


# Singleton
dockerManager = DockerManager()
