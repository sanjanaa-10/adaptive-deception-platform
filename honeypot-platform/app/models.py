from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Decoy(Base):
    __tablename__ = "decoys"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    service_type = Column(String, nullable=False)  # e.g. SSH, HTTP, FTP
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    status = Column(String, default="active")  # active / inactive
    adaptive_profile = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sessions = relationship("SessionModel", back_populates="decoy")
    deception_profiles = relationship("DeceptionProfile", back_populates="decoy")


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    decoy_id = Column(Integer, ForeignKey("decoys.id"), nullable=False)
    attacker_ip = Column(String, nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)

    decoy = relationship("Decoy", back_populates="sessions")
    events = relationship("Event", back_populates="session")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String, nullable=False)  # login_attempt, command_exec, file_access
    payload = Column(Text, nullable=True)
    risk_score = Column(Float, default=0.0)

    session = relationship("SessionModel", back_populates="events")
    alerts = relationship("Alert", back_populates="event")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    severity = Column(String, default="low")  # low / medium / high / critical
    message = Column(String, nullable=False)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    event = relationship("Event", back_populates="alerts")


class DeceptionProfile(Base):
    __tablename__ = "deception_profiles"

    id = Column(Integer, primary_key=True, index=True)
    decoy_id = Column(Integer, ForeignKey("decoys.id"), nullable=False)
    trigger_condition = Column(String, nullable=False)  # e.g. "recon_detected"
    adaptation_rule = Column(String, nullable=False)  # e.g. "switch_to_high_interaction"
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    decoy = relationship("Decoy", back_populates="deception_profiles")
