import datetime
from enum import Enum
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

from .env import get_env
from .logger import get_logger

__all__ = (
    "Table",
)

logger = get_logger()

class Table(str, Enum):
    PLAYERS = "players"
    LEAGUES = "leagues"
    PLAYER_LEAGUES = "player_leagues"

# Base model
class Base(DeclarativeBase):
    pass

class LeagueTable(Base):
    __tablename__ = Table.LEAGUES.value

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    teams: Mapped[dict] = mapped_column(JSONB, default=dict)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)

class PlayerTable(Base):
    __tablename__ = Table.PLAYERS.value

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

class PlayerLeagueTable(Base):
    __tablename__ = Table.PLAYER_LEAGUES.value
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
    engine = create_engine(get_env("DATABASE_URL"), echo=False)

    logger.info(f"Missing tables detected: {missing_tables}")
    Base.metadata.create_all(bind=engine)
    logger.info("Missing tables created.")