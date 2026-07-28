from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


# ---- Auth ----
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- Decoys ----
class DecoyCreate(BaseModel):
    name: str
    service_type: str
    ip: str
    port: int
    adaptive_profile: Optional[Dict[str, Any]] = {}


class DecoyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    adaptive_profile: Optional[Dict[str, Any]] = None


class DecoyOut(BaseModel):
    id: int
    name: str
    service_type: str
    ip: str
    port: int
    status: str
    adaptive_profile: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Events (pushed by the honeypot sensor) ----
class EventCreate(BaseModel):
    decoy_id: int
    attacker_ip: str
    event_type: str
    payload: Optional[str] = None
    risk_score: Optional[float] = 0.0


class EventOut(BaseModel):
    id: int
    session_id: int
    timestamp: datetime
    event_type: str
    payload: Optional[str]
    risk_score: float

    class Config:
        from_attributes = True


# ---- Alerts ----
class AlertOut(BaseModel):
    id: int
    event_id: int
    severity: str
    message: str
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    resolved: bool
