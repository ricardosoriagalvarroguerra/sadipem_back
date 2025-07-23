from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import crud, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/datos", response_model=list[schemas.DatosSadipemSchema])
def read_datos(region: str = None, sector: str = None, db: Session = Depends(get_db)):
    return crud.get_datos(db, region, sector)

@router.get("/api/regiones", response_model=schemas.RegionResponse)
def read_regiones(db: Session = Depends(get_db)):
    return {"regiones": crud.get_regiones(db)}

@router.get("/api/sectores", response_model=schemas.SectorResponse)
def read_sectores(db: Session = Depends(get_db)):
    return {"sectores": crud.get_sectores(db)}

@router.get("/api/stats")
def read_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)

@router.get("/api/valores_ente")
def read_valores_ente(db: Session = Depends(get_db)):
    return crud.get_valores_por_ente(db)
