from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base


class HCP(Base):
    __tablename__ = "hcps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    specialty: Mapped[str] = mapped_column(String(120), default="")
    organization: Mapped[str] = mapped_column(String(180), default="")
    city: Mapped[str] = mapped_column(String(100), default="")
