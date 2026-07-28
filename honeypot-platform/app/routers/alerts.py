from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[schemas.AlertOut])
def list_alerts(resolved: bool = None, db: Session = Depends(get_db)):
    query = db.query(models.Alert)
    if resolved is not None:
        query = query.filter(models.Alert.resolved == resolved)
    return query.order_by(models.Alert.created_at.desc()).all()


@router.patch("/{alert_id}", response_model=schemas.AlertOut)
def update_alert(alert_id: int, update: schemas.AlertUpdate, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved = update.resolved
    db.commit()
    db.refresh(alert)
    return alert
