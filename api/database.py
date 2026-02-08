"""
Database configuration and ORM models using SQLAlchemy.
Supports both SQLite (local) and PostgreSQL (production).
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from api.config import settings

# Determine database URL
# Prioritize env var, fall back to local sqlite file
DATABASE_URL = settings.database_url or "sqlite:///bets.db"

# Handle capitalization for postgres (SQLAlchemy requires postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"🔌 Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

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
    validation_source = Column(String, default="manual")
    notes = Column(Text, nullable=True)


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
    print("✅ Database tables initialized")

if __name__ == "__main__":
    init_db()
