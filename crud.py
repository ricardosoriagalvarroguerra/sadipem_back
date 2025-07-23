from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from collections import defaultdict
from models import DatosSadipem

def get_datos(db: Session, region: str = None, sector: str = None):
    year_col = cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer)
    query = db.query(DatosSadipem)
    # Filtro por año de fecha_contratacion entre 2018 y 2024
    query = query.filter(
        year_col >= 2018,
        year_col <= 2024
    )
    if region:
        query = query.filter(DatosSadipem.região == region)
    if sector:
        query = query.filter(DatosSadipem.sector == sector)
    return query.all()

def get_regiones(db: Session):
    return [r[0] for r in db.query(DatosSadipem.região).distinct().all() if r[0]]

def get_sectores(db: Session):
    return [s[0] for s in db.query(DatosSadipem.sector).distinct().all() if s[0]]

def get_stats(db: Session):
    total_por_region = db.query(DatosSadipem.região, func.sum(DatosSadipem.valor_usd)).group_by(DatosSadipem.região).all()
    total_por_sector = db.query(DatosSadipem.sector, func.sum(DatosSadipem.valor_usd)).group_by(DatosSadipem.sector).all()
    return {
        "total_por_region": [{"region": r, "total_usd": t} for r, t in total_por_region],
        "total_por_sector": [{"sector": s, "total_usd": t} for s, t in total_por_sector],
    }

def get_valores_por_ente(db: Session):
    year_col = cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer)
    common_filters = [
        DatosSadipem.garantia_soberana == 'Si',
        DatosSadipem.tiempo_prestamo > 14,
        year_col >= 2019,
        year_col <= 2024,
    ]

    # Totales por ente
    resultados = (
        db.query(
            DatosSadipem.tipo_ente,
            DatosSadipem.ente,
            DatosSadipem.garantia_soberana,
            func.sum(DatosSadipem.valor_usd).label('total_usd')
        )
        .filter(*common_filters)
        .group_by(DatosSadipem.tipo_ente, DatosSadipem.ente, DatosSadipem.garantia_soberana)
        .all()
    )

    # Top 5 financiadores por ente utilizando funciones de ventana
    subq_fin = (
        db.query(
            DatosSadipem.ente.label('ente'),
            DatosSadipem.nombre_acreedor.label('nombre_acreedor'),
            func.sum(DatosSadipem.valor_usd).label('total_usd'),
            func.row_number().over(
                partition_by=DatosSadipem.ente,
                order_by=func.sum(DatosSadipem.valor_usd).desc()
            ).label('rn')
        )
        .filter(*common_filters)
        .group_by(DatosSadipem.ente, DatosSadipem.nombre_acreedor)
    ).subquery()

    top_financiadores_dict = defaultdict(list)
    for row in db.query(subq_fin).filter(subq_fin.c.rn <= 5).all():
        top_financiadores_dict[row.ente].append({
            'nombre_acreedor': row.nombre_acreedor,
            'total_usd': row.total_usd
        })

    # Top 5 sectores por ente utilizando funciones de ventana
    subq_sec = (
        db.query(
            DatosSadipem.ente.label('ente'),
            DatosSadipem.sector.label('sector'),
            func.sum(DatosSadipem.valor_usd).label('total_usd'),
            func.row_number().over(
                partition_by=DatosSadipem.ente,
                order_by=func.sum(DatosSadipem.valor_usd).desc()
            ).label('rn')
        )
        .filter(*common_filters)
        .group_by(DatosSadipem.ente, DatosSadipem.sector)
    ).subquery()

    top_sectores_dict = defaultdict(list)
    for row in db.query(subq_sec).filter(subq_sec.c.rn <= 5).all():
        top_sectores_dict[row.ente].append({
            'sector': row.sector,
            'total_usd': row.total_usd
        })

    return [
        {
            'tipo_ente': tipo_ente,
            'ente': ente,
            'garantia_soberana': garantia_soberana,
            'total_usd': total_usd,
            'top_financiadores': top_financiadores_dict.get(ente, []),
            'top_sectores': top_sectores_dict.get(ente, [])
        }
        for tipo_ente, ente, garantia_soberana, total_usd in resultados
    ]
