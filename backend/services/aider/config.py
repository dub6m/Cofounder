"""
Aider Agent Configuration — initializes Aider with the correct context
for the Cofounder execution pipeline.

Key design decisions:
  - Uses --read flag for TARGET_ARCHITECTURE.md (read-only contract)
  - Prompt Caching enabled to reduce SiliconFlow RPM burn
  - Model set to SiliconFlow Qwen2.5-Coder-7B via OpenAI-compatible endpoint
  - Workspace directory is the sandbox /workspace mount point
"""

import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)


class AiderConfig:
    """
    Builds and manages the Aider agent configuration.

    The Aider agent is invoked as a subprocess inside the Docker sandbox.
    This class constructs the CLI flags and environment variables needed
    to run Aider with the correct model, context, and caching settings.
    """

    def __init__(
        self,
        workspaceDir: str,
        architectureFile: Optional[str] = None,
    ):
        """
        Args:
            workspaceDir: Absolute path to the project workspace.
            architectureFile: Filename of the architecture contract
                              (defaults to settings.aider_architecture_file).
        """
        self.workspaceDir = Path(workspaceDir)
        self.architectureFile = architectureFile or settings.aider_architecture_file
        self.model = settings.aider_model
        self.promptCaching = settings.aider_prompt_caching

    @property
    def architecturePath(self) -> Path:
        """Full path to the architecture contract file."""
        return self.workspaceDir / self.architectureFile

    def ensureArchitectureFile(self, content: str = "") -> Path:
        """
        Create the TARGET_ARCHITECTURE.md file in the workspace
        if it doesn't already exist.
        """
        path = self.architecturePath
        if not path.exists():
            path.write_text(content or "# Target Architecture\n\n(pending)\n")
            logger.info(f"Created architecture file: {path}")
        return path

    def buildCliArgs(self, editInstruction: str) -> list[str]:
        """
        Build the Aider CLI argument list.

        Returns a list of strings suitable for subprocess.run().
        Flags used:
          --model:    The SiliconFlow Qwen2.5 model
          --read:     TARGET_ARCHITECTURE.md as read-only context
          --message:  The edit instruction from the orchestrator
          --yes:      Auto-confirm all edits (non-interactive)
          --no-git:   Don't auto-commit (we handle git ourselves)
          --cache-prompts: Enable prompt caching for rate-limit efficiency
        """
        args = [
            "aider",
            "--model", f"openai/{self.model}",
            "--read", str(self.architecturePath),
            "--message", editInstruction,
            "--yes",
            "--no-git",
        ]

        if self.promptCaching:
            args.append("--cache-prompts")

        return args

    def buildEnv(self) -> dict[str, str]:
        """
        Build the environment variables dict for the Aider subprocess.

        Routes through SiliconFlow's OpenAI-compatible endpoint
        so Aider thinks it's talking to OpenAI.
        """
        env = os.environ.copy()
        env.update({
            "OPENAI_API_KEY": settings.siliconflow_api_key,
            "OPENAI_API_BASE": settings.siliconflow_base_url,
        })
        return env

    async def runEdit(
        self,
        instruction: str,
        targetFiles: Optional[list[str]] = None,
    ) -> dict:
        """
        Execute an Aider edit in the workspace.

        Args:
            instruction: Natural language edit instruction.
            targetFiles: Optional list of specific files to edit.
                         If not provided, Aider will auto-detect.

        Returns:
            dict with exit_code, stdout, and stderr.
        """
        import asyncio

        # Build args
        args = self.buildCliArgs(instruction)

        # Append target files if specified
        if targetFiles:
            args.extend(targetFiles)

        logger.info(
            f"Running Aider: model={self.model}, "
            f"caching={'on' if self.promptCaching else 'off'}, "
            f"workspace={self.workspaceDir}"
        )
        logger.debug(f"Aider args: {' '.join(args)}")

        # Run as async subprocess
        def _run():
            result = subprocess.run(
                args,
                cwd=str(self.workspaceDir),
                env=self.buildEnv(),
                capture_output=True,
                text=True,
                timeout=settings.sandbox_timeout,
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        return await asyncio.to_thread(_run)


def createAiderConfig(
    workspaceDir: str,
    architectureContent: Optional[str] = None,
) -> AiderConfig:
    """
    Factory function to create an AiderConfig instance
    and ensure the workspace is ready.

    Args:
        workspaceDir: Path to the workspace directory.
        architectureContent: Optional initial content for the
                             TARGET_ARCHITECTURE.md file.
    """
    config = AiderConfig(workspaceDir=workspaceDir)

    if architectureContent:
        config.ensureArchitectureFile(content=architectureContent)

    return config
