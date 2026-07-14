from datetime import date, datetime, time
from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    hcp_id: Mapped[int] = mapped_column(ForeignKey("hcps.id"), index=True)
    interaction_type: Mapped[str] = mapped_column(String(60), default="Meeting")
    interaction_date: Mapped[date] = mapped_column(Date)
    interaction_time: Mapped[time] = mapped_column(Time)
    attendees: Mapped[str] = mapped_column(Text, default="")
    topics_discussed: Mapped[str] = mapped_column(Text, default="")
    materials_shared: Mapped[str] = mapped_column(Text, default="")
    samples_distributed: Mapped[str] = mapped_column(Text, default="")
    sentiment: Mapped[str] = mapped_column(String(30), default="Neutral")
    outcomes: Mapped[str] = mapped_column(Text, default="")
    follow_up_actions: Mapped[str] = mapped_column(Text, default="")
    ai_summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    hcp = relationship("HCP")
