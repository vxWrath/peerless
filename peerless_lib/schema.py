import datetime
import os
import time

import sqlalchemy.exc
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
    create_engine,
    inspect,
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

def wait_for_db(url: str, retries: int = 3, delay: int = 10):
    time.sleep(delay)

    for _ in range(retries):
        try:
            engine = create_engine(url, echo=False)

            conn = engine.connect()
            conn.close()

            logger.info("Database is ready!")
            return engine
        except sqlalchemy.exc.OperationalError:
            time.sleep(delay)

    raise RuntimeError("Database connection failed")

def create_tables() -> None:
    url = os.getenv("DATABASE_URL", "")
    engine = wait_for_db(url)

    logger.info("Checking if tables exist...")
    with engine.connect() as conn:
        inspector = inspect(conn)
        existing_tables = inspector.get_table_names()
        all_tables = set(Base.metadata.tables.keys())
        missing_tables = all_tables - set(existing_tables)

        if missing_tables:
            logger.info(f"Missing tables detected: {missing_tables}")
            Base.metadata.create_all(bind=engine)
            logger.info("Missing tables created.")
        else:
            logger.info("All tables already exist. No action taken.")