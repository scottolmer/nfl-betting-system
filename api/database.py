"""
Database configuration and ORM models using SQLAlchemy.
Supports both SQLite (local) and PostgreSQL (production).
"""

import os
import json
from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime, Text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from api.config import settings
import uuid
import enum

# Determine database URL
# Prioritize env var, fall back to local sqlite file
DATABASE_URL = settings.database_url or "sqlite:///bets.db"

# Handle capitalization for postgres (SQLAlchemy requires postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# Create engine
# check_same_thread=False is needed for SQLite with FastAPI
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# --- Models ---

class Parlay(Base):
    """
    Represents a generated parlay bet.
    """
    __tablename__ = "parlays"

    parlay_id = Column(String, primary_key=True)
    created_date = Column(String)  # ISO format date string
    week = Column(Integer)
    confidence_score = Column(Float)
    odds = Column(Float, nullable=True)
    parlay_type = Column(String, default="standard")
    status = Column(String, default="pending")  # pending, won, lost
    agent_breakdown = Column(JSON, default={})  # Stored as JSON
    dependencies = Column(JSON, default={})     # Stored as JSON
    created_timestamp = Column(Float, default=lambda: datetime.now().timestamp())
    
    # Relationships
    legs = relationship("Leg", back_populates="parlay", cascade="all, delete-orphan")
    calibration_results = relationship("CalibrationResult", back_populates="parlay", uselist=False)

    def to_dict(self):
        """Convert to dictionary for API/UI"""
        return {
            "parlay_id": self.parlay_id,
            "week": self.week,
            "confidence_score": self.confidence_score,
            "odds": self.odds,
            "parlay_type": self.parlay_type,
            "status": self.status,
            "agent_breakdown": self.agent_breakdown,
            "timestamp": self.created_timestamp,
            "legs": [leg.to_dict() for leg in self.legs]
        }


class Leg(Base):
    """
    Represents a single leg (bet) within a parlay.
    """
    __tablename__ = "legs"

    leg_id = Column(String, primary_key=True)
    parlay_id = Column(String, ForeignKey("parlays.parlay_id"))
    player = Column(String)
    team = Column(String)
    prop_type = Column(String)
    bet_type = Column(String)
    line = Column(Float)
    agent_scores = Column(JSON, default={})  # Stored as JSON
    result = Column(Integer, nullable=True)  # 1 for Hit, 0 for Miss, None for Pending

    # Relationship
    parlay = relationship("Parlay", back_populates="legs")

    def to_dict(self):
        return {
            "player": self.player,
            "team": self.team,
            "prop_type": self.prop_type,
            "bet_type": self.bet_type,
            "line": self.line,
            "result": self.result
        }


class CalibrationResult(Base):
    """
    Stores calibration analysis comparing predicted vs actual results.
    """
    __tablename__ = "calibration_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parlay_id = Column(String, ForeignKey("parlays.parlay_id"))
    confidence_predicted = Column(Float)
    confidence_actual = Column(Float)
    calibration_error = Column(Float)
    notes = Column(Text, nullable=True)

    # Relationship
    parlay = relationship("Parlay", back_populates="calibration_results")


class PropAvailability(Base):
    """
    Tracks availability of props (e.g. from DraftKings Pick6).
    Used by validation system.
    """
    __tablename__ = "prop_availability"

    id = Column(String, primary_key=True)  # prop_signature
    player = Column(String)
    prop_type = Column(String)
    bet_type = Column(String)
    line = Column(Float)
    is_available = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.now)
    validation_source = Column(String, default='auto')  # 'auto' or 'manual'
    notes = Column(String)


class GameDataFile(Base):
    """
    Stores raw CSV data files uploaded via Admin UI.
    Acts as the source of truth for analysis, replacing local file storage.
    """
    __tablename__ = "game_data_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    week = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)  # e.g., 'betting_lines', 'dvoa_offense'
    filename = Column(String)
    content = Column(String)  # Storing as Text. For very large files, consider LargeBinary/Blob.
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Composite index for faster lookups
    __table_args__ = (
        Index('idx_week_type', 'week', 'file_type'),
    )

class PropValidationRule(Base):
    """
    Represents an invalid prop combination rule.
    """
    __tablename__ = "prop_validation_rules"

    rule_id = Column(String, primary_key=True)
    description = Column(String)
    rule_type = Column(String)  # 'same_player_props', 'stat_correlation', 'platform_restriction'
    conditions = Column(JSON)   # Flexible dict for different rule types
    auto_applied = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)
    times_triggered = Column(Integer, default=0)


class ParlayValidationHistory(Base):
    """
    History of parlay validations.
    """
    __tablename__ = "parlay_validation_history"

    validation_id = Column(Integer, primary_key=True, autoincrement=True)
    parlay_signature = Column(String)
    props_json = Column(JSON)
    is_valid = Column(Boolean)
    invalid_reason = Column(String, nullable=True)
    validated_date = Column(DateTime, default=datetime.now)
    week = Column(Integer)


# --- Sprint 1: New Models ---

class AppMode(str, enum.Enum):
    DFS = "dfs"
    PROPS = "props"
    FANTASY = "fantasy"


class Player(Base):
    """NFL player with ESPN headshot data."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    team = Column(String, nullable=False, index=True)
    position = Column(String, nullable=False)
    espn_id = Column(String, nullable=True, unique=True)
    headshot_url = Column(String, nullable=True)
    status = Column(String, default="active")  # active, injured, inactive
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    projections = relationship("PlayerProjection", back_populates="player", cascade="all, delete-orphan")
    book_odds = relationship("BookOdds", back_populates="player", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_player_name_team', 'name', 'team'),
    )


class User(Base):
    """App user with subscription info."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    subscription_tier = Column(String, default="free")  # free, trial, premium
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    bets = relationship("UserBet", back_populates="user", cascade="all, delete-orphan")


class UserBet(Base):
    """User-placed bet across all modes (DFS, Props, Fantasy)."""
    __tablename__ = "user_bets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(String, nullable=False)  # dfs, props, fantasy
    platform = Column(String, nullable=True)  # PrizePicks, Underdog, DraftKings, etc.
    week = Column(Integer, nullable=False)
    legs = Column(JSON, default=[])  # Array of leg objects
    status = Column(String, default="pending")  # pending, placed, won, lost, push
    confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    user = relationship("User", back_populates="bets")

    __table_args__ = (
        Index('idx_user_bet_week', 'user_id', 'week'),
    )


class PlayerProjection(Base):
    """Engine-generated projection for a player prop."""
    __tablename__ = "player_projections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    week = Column(Integer, nullable=False)
    stat_type = Column(String, nullable=False)  # pass_yds, rush_yds, receptions, etc.
    implied_line = Column(Float, nullable=True)  # Derived from odds pricing
    engine_projection = Column(Float, nullable=True)  # Our adjusted projection
    confidence = Column(Float, nullable=True)  # 0-100
    direction = Column(String, nullable=True)  # OVER, UNDER, AVOID
    agent_breakdown = Column(JSON, default={})  # Per-agent scores and reasoning
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationship
    player = relationship("Player", back_populates="projections")

    __table_args__ = (
        Index('idx_projection_player_week', 'player_id', 'week'),
        Index('idx_projection_week_stat', 'week', 'stat_type'),
    )


class BookOdds(Base):
    """Odds from a specific bookmaker for a player prop."""
    __tablename__ = "book_odds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    week = Column(Integer, nullable=False)
    stat_type = Column(String, nullable=False)
    bookmaker = Column(String, nullable=False)  # draftkings, fanduel, betmgm, etc.
    line = Column(Float, nullable=False)
    over_price = Column(Integer, nullable=True)  # American odds e.g. -110, +100
    under_price = Column(Integer, nullable=True)
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    player = relationship("Player", back_populates="book_odds")

    __table_args__ = (
        Index('idx_book_odds_player_week', 'player_id', 'week', 'stat_type'),
        Index('idx_book_odds_bookmaker', 'bookmaker', 'week'),
    )


class LineMovement(Base):
    """Historical line movement tracking."""
    __tablename__ = "line_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    week = Column(Integer, nullable=False)
    stat_type = Column(String, nullable=False)
    bookmaker = Column(String, nullable=False)
    line = Column(Float, nullable=False)
    over_price = Column(Integer, nullable=True)
    under_price = Column(Integer, nullable=True)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index('idx_line_movement_player_week', 'player_id', 'week', 'stat_type'),
    )


# --- Dependency ---

def get_db():
    """Generator for database session (for FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized")

if __name__ == "__main__":
    init_db()
