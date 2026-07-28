from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/decoys", tags=["decoys"])


@router.get("/", response_model=List[schemas.DecoyOut])
def list_decoys(db: Session = Depends(get_db)):
    return db.query(models.Decoy).all()


@router.post("/", response_model=schemas.DecoyOut)
def create_decoy(decoy: schemas.DecoyCreate, db: Session = Depends(get_db)):
    new_decoy = models.Decoy(**decoy.dict())
    db.add(new_decoy)
    db.commit()
    db.refresh(new_decoy)
    return new_decoy


@router.patch("/{decoy_id}", response_model=schemas.DecoyOut)
def update_decoy(decoy_id: int, updates: schemas.DecoyUpdate, db: Session = Depends(get_db)):
    decoy = db.query(models.Decoy).filter(models.Decoy.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(decoy, field, value)

    db.commit()
    db.refresh(decoy)
    return decoy


@router.delete("/{decoy_id}")
def delete_decoy(decoy_id: int, db: Session = Depends(get_db)):
    decoy = db.query(models.Decoy).filter(models.Decoy.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy not found")
    db.delete(decoy)
    db.commit()
    return {"detail": "Decoy deleted"}


@router.post("/{decoy_id}/adapt")
def adapt_decoy(decoy_id: int, db: Session = Depends(get_db)):
    decoy = db.query(models.Decoy).filter(models.Decoy.id == decoy_id).first()
    if not decoy:
        raise HTTPException(status_code=404, detail="Decoy not found")

    profile = dict(decoy.adaptive_profile or {})
    profile["last_adaptation"] = "triggered"
    decoy.adaptive_profile = profile
    db.commit()
    db.refresh(decoy)
    return {"detail": f"Decoy {decoy_id} adapted", "profile": decoy.adaptive_profile}