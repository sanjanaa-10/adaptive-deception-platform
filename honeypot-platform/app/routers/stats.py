from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app import models

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_decoys = db.query(models.Decoy).count()
    active_decoys = db.query(models.Decoy).filter(models.Decoy.status == "active").count()
    total_sessions = db.query(models.SessionModel).count()
    total_events = db.query(models.Event).count()
    open_alerts = db.query(models.Alert).filter(models.Alert.resolved == False).count()  # noqa: E712

    top_attackers = (
        db.query(models.SessionModel.attacker_ip, func.count(models.SessionModel.id).label("count"))
        .group_by(models.SessionModel.attacker_ip)
        .order_by(func.count(models.SessionModel.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_decoys": total_decoys,
        "active_decoys": active_decoys,
        "total_sessions": total_sessions,
        "total_events": total_events,
        "open_alerts": open_alerts,
        "top_attackers": [{"ip": ip, "attempts": count} for ip, count in top_attackers],
    }


@router.get("/timeseries")
def timeseries(days: int = 7, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date(models.Event.timestamp).label("day"),
            func.count(models.Event.id).label("count"),
        )
        .filter(models.Event.timestamp >= since)
        .group_by(func.date(models.Event.timestamp))
        .order_by(func.date(models.Event.timestamp))
        .all()
    )
    return [{"day": str(day), "count": count} for day, count in rows]
