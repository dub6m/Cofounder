"""
SQLAlchemy ORM models matching the database schema from IMPLEMENTATION_PLAN.md.
Uses generic types compatible with both PostgreSQL and SQLite.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


def utcNow() -> datetime:
    return datetime.now(timezone.utc)


def newUuid() -> str:
    return str(uuid.uuid4())


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=newUuid
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phase: Mapped[str] = mapped_column(
        String(50), nullable=False, default="negotiation"
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcNow
    )
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcNow, onupdate=utcNow
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.createdAt"
    )
    architectureSnapshots: Mapped[list["ArchitectureSnapshot"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    builds: Mapped[list["Build"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=newUuid
    )
    conversationId: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, nullable=True
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcNow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class ArchitectureSnapshot(Base):
    __tablename__ = "architecture_snapshots"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=newUuid
    )
    conversationId: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    flowchart: Mapped[str | None] = mapped_column(Text, nullable=True)
    erd: Mapped[str | None] = mapped_column(Text, nullable=True)
    sequence: Mapped[str | None] = mapped_column(Text, nullable=True)
    isFinalized: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcNow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        back_populates="architectureSnapshots"
    )
    builds: Mapped[list["Build"]] = relationship(back_populates="snapshot")


class Build(Base):
    __tablename__ = "builds"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=newUuid
    )
    conversationId: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    snapshotId: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("architecture_snapshots.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending"
    )
    exitCode: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stderrTail: Mapped[str | None] = mapped_column(Text, nullable=True)
    scoutReport: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dockerImage: Mapped[str | None] = mapped_column(String(255), nullable=True)
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcNow
    )
    completedAt: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="builds")
    snapshot: Mapped["ArchitectureSnapshot"] = relationship(back_populates="builds")
    deployment: Mapped["Deployment | None"] = relationship(
        back_populates="build", uselist=False
    )


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=newUuid
    )
    buildId: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("builds.id"),
        nullable=False,
    )
    repoUrl: Mapped[str] = mapped_column(String(512), nullable=False)
    commitHash: Mapped[str | None] = mapped_column(String(40), nullable=True)
    branch: Mapped[str] = mapped_column(
        String(100), nullable=False, default="main"
    )
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending"
    )
    createdAt: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcNow
    )

    # Relationships
    build: Mapped["Build"] = relationship(back_populates="deployment")
