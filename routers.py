from fastapi import APIRouter, Depends
from fastapi import HTTPException
import logging
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
import json
import redis
from database import SessionLocal
from cache import redis_client
import crud, schemas

logger = logging.getLogger(__name__)

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
    cached = None
    if redis_client:
        try:
            cached = redis_client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis error getting %s: %s", key, exc)
    if cached:
        return json.loads(cached)
    data = crud.get_datos(db, region, sector)
    if redis_client:
        try:
            redis_client.set(key, json.dumps(jsonable_encoder(data)), ex=300)
        except redis.RedisError as exc:
            logger.warning("Redis error setting %s: %s", key, exc)
    return data

@router.get("/api/regiones", response_model=schemas.RegionResponse)
def read_regiones(db: Session = Depends(get_db)):
    key = "regiones"
    cached = None
    if redis_client:
        try:
            cached = redis_client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis error getting %s: %s", key, exc)
    if cached:
        return json.loads(cached)
    regiones = {"regiones": crud.get_regiones(db)}
    if redis_client:
        try:
            redis_client.set(key, json.dumps(jsonable_encoder(regiones)), ex=300)
        except redis.RedisError as exc:
            logger.warning("Redis error setting %s: %s", key, exc)
    return regiones

@router.get("/api/sectores", response_model=schemas.SectorResponse)
def read_sectores(db: Session = Depends(get_db)):
    key = "sectores"
    cached = None
    if redis_client:
        try:
            cached = redis_client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis error getting %s: %s", key, exc)
    if cached:
        return json.loads(cached)
    sectores = {"sectores": crud.get_sectores(db)}
    if redis_client:
        try:
            redis_client.set(key, json.dumps(jsonable_encoder(sectores)), ex=300)
        except redis.RedisError as exc:
            logger.warning("Redis error setting %s: %s", key, exc)
    return sectores

@router.get("/api/stats")
def read_stats(db: Session = Depends(get_db)):
    key = "stats"
    cached = None
    if redis_client:
        try:
            cached = redis_client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis error getting %s: %s", key, exc)
    if cached:
        return json.loads(cached)
    stats = crud.get_stats(db)
    if redis_client:
        try:
            redis_client.set(key, json.dumps(jsonable_encoder(stats)), ex=300)
        except redis.RedisError as exc:
            logger.warning("Redis error setting %s: %s", key, exc)
    return stats

@router.get("/api/valores_ente")
def read_valores_ente(db: Session = Depends(get_db)):
    key = "valores_ente"
    cached = None
    if redis_client:
        try:
            cached = redis_client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis error getting %s: %s", key, exc)
    if cached:
        return json.loads(cached)
    valores = crud.get_valores_por_ente(db)
    if redis_client:
        try:
            redis_client.set(key, json.dumps(jsonable_encoder(valores)), ex=300)
        except redis.RedisError as exc:
            logger.warning("Redis error setting %s: %s", key, exc)
    return valores


@router.get("/api/interno_externo_sector/{year}", response_model=list[schemas.InternoExternoSectorSchema])
def read_interno_externo_sector(year: int, db: Session = Depends(get_db)):
    key = f"interno_externo_sector:{year}"
    cached = None
    if redis_client:
        try:
            cached = redis_client.get(key)
        except redis.RedisError as exc:
            logger.warning("Redis error getting %s: %s", key, exc)
    if cached:
        return json.loads(cached)
    data = crud.get_interno_externo_por_sector(db, year)
    if redis_client:
        try:
            redis_client.set(key, json.dumps(jsonable_encoder(data)), ex=300)
        except redis.RedisError as exc:
            logger.warning("Redis error setting %s: %s", key, exc)
    return data
