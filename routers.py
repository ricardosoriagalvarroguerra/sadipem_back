from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import json
from database import SessionLocal
from cache import redis_client
import crud, schemas

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/datos", response_model=list[schemas.DatosSadipemSchema])
def read_datos(region: str | None = None, sector: str | None = None, db: Session = Depends(get_db)):
    key = f"datos:{region}:{sector}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    data = crud.get_datos(db, region, sector)
    redis_client.set(key, json.dumps(jsonable_encoder(data)), ex=300)
    return data

@router.get("/api/regiones", response_model=schemas.RegionResponse)
def read_regiones(db: Session = Depends(get_db)):
    key = "regiones"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    regiones = {"regiones": crud.get_regiones(db)}
    redis_client.set(key, json.dumps(jsonable_encoder(regiones)), ex=300)
    return regiones

@router.get("/api/sectores", response_model=schemas.SectorResponse)
def read_sectores(db: Session = Depends(get_db)):
    key = "sectores"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    sectores = {"sectores": crud.get_sectores(db)}
    redis_client.set(key, json.dumps(jsonable_encoder(sectores)), ex=300)
    return sectores

@router.get("/api/stats")
def read_stats(db: Session = Depends(get_db)):
    key = "stats"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    stats = crud.get_stats(db)
    redis_client.set(key, json.dumps(jsonable_encoder(stats)), ex=300)
    return stats

@router.get("/api/valores_ente")
def read_valores_ente(db: Session = Depends(get_db)):
    key = "valores_ente"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    valores = crud.get_valores_por_ente(db)
    redis_client.set(key, json.dumps(jsonable_encoder(valores)), ex=300)
    return valores
