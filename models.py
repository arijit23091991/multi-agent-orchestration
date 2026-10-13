from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ResearchRun(Base):
    __tablename__ = "research_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    topic: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    search_results: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    scraped_content: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    report: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    feedback: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )