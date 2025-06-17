import datetime
import os
from typing import List

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
    create_engine,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .logger import get_logger

logger = get_logger()

# Base model
class Base(DeclarativeBase):
    pass

# League table
class LeagueTable(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    teams: Mapped[dict] = mapped_column(JSONB, default=dict)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)

# Player table
class PlayerTable(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

# Association table
class PlayerLeagueTable(Base):
    __tablename__ = "player_leagues"
    __table_args__ = (
        PrimaryKeyConstraint("player_id", "league_id"),
    )

    player_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    league_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False)

    demands: Mapped[dict] = mapped_column(JSONB, default=dict)
    suspension: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    contract: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    appointed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    waitlisted_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)

def create_missing_tables(missing_tables: List[str]) -> None:
    engine = create_engine(os.getenv("DATABASE_URL", ""), echo=False)

    logger.info(f"Missing tables detected: {missing_tables}")
    Base.metadata.create_all(bind=engine)
    logger.info("Missing tables created.")