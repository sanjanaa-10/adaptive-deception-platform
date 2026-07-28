from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["events"])

RISK_ALERT_THRESHOLD = 0.7


@router.post("/events", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    decoy = db.query(models.Decoy).filter(models.Decoy.id == event.decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy not found")

    # find an open session for this attacker+decoy, or start a new one
    session = (
        db.query(models.SessionModel)
        .filter(
            models.SessionModel.decoy_id == event.decoy_id,
            models.SessionModel.attacker_ip == event.attacker_ip,
            models.SessionModel.end_time.is_(None),
        )
        .first()
    )
    if not session:
        session = models.SessionModel(decoy_id=event.decoy_id, attacker_ip=event.attacker_ip)
        db.add(session)
        db.commit()
        db.refresh(session)

    new_event = models.Event(
        session_id=session.id,
        event_type=event.event_type,
        payload=event.payload,
        risk_score=event.risk_score,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    # auto-generate an alert if risk is high
    if new_event.risk_score >= RISK_ALERT_THRESHOLD:
        alert = models.Alert(
            event_id=new_event.id,
            severity="high" if new_event.risk_score < 0.9 else "critical",
            message=f"High-risk {new_event.event_type} from {event.attacker_ip}",
        )
        db.add(alert)
        db.commit()

    return new_event


@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.SessionModel).all()


@router.get("/sessions/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.SessionModel).filter(models.SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/events", response_model=List[schemas.EventOut])
def list_events(session_id: int = None, decoy_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Event)
    if session_id:
        query = query.filter(models.Event.session_id == session_id)
    if decoy_id:
        query = query.join(models.SessionModel).filter(models.SessionModel.decoy_id == decoy_id)
    return query.all()
