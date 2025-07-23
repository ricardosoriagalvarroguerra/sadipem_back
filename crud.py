from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models import DatosSadipem

def get_datos(db: Session, region: str = None, sector: str = None):
    from sqlalchemy import cast, Integer
    query = db.query(DatosSadipem)
    # Filtro por año de fecha_contratacion entre 2018 y 2024
    query = query.filter(
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) >= 2018,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) <= 2024
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
    from sqlalchemy import case, desc, cast, Integer
    # Filtra por garantia_soberana = 'Si', tiempo_prestamo > 14 y año entre 2019 y 2024
    query = db.query(
        DatosSadipem.tipo_ente,
        DatosSadipem.ente,
        DatosSadipem.garantia_soberana,
        func.sum(DatosSadipem.valor_usd)
    ).filter(
        DatosSadipem.garantia_soberana == 'Si',
        DatosSadipem.tiempo_prestamo > 14,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) >= 2019,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) <= 2024
    ).group_by(DatosSadipem.tipo_ente, DatosSadipem.ente, DatosSadipem.garantia_soberana)
    resultados = query.all()

    # Para cada ente, obtener el top 5 financiadores
    top_financiadores_dict = {}
    subq = db.query(
        DatosSadipem.ente,
        DatosSadipem.nombre_acreedor,
        func.sum(DatosSadipem.valor_usd).label('total_usd')
    ).filter(
        DatosSadipem.garantia_soberana == 'Si',
        DatosSadipem.tiempo_prestamo > 14,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) >= 2019,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) <= 2024
    ).group_by(DatosSadipem.ente, DatosSadipem.nombre_acreedor).subquery()

    for row in db.query(subq.c.ente, subq.c.nombre_acreedor, subq.c.total_usd).order_by(subq.c.ente, desc(subq.c.total_usd)):
        if row.ente not in top_financiadores_dict:
            top_financiadores_dict[row.ente] = []
        if len(top_financiadores_dict[row.ente]) < 5:
            top_financiadores_dict[row.ente].append({
                'nombre_acreedor': row.nombre_acreedor,
                'total_usd': row.total_usd
            })

    # Para cada ente, obtener el top 5 sectores
    top_sectores_dict = {}
    subq_sector = db.query(
        DatosSadipem.ente,
        DatosSadipem.sector,
        func.sum(DatosSadipem.valor_usd).label('total_usd')
    ).filter(
        DatosSadipem.garantia_soberana == 'Si',
        DatosSadipem.tiempo_prestamo > 14,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) >= 2019,
        cast(func.substr(DatosSadipem.fecha_contratacion, 1, 4), Integer) <= 2024
    ).group_by(DatosSadipem.ente, DatosSadipem.sector).subquery()

    for row in db.query(subq_sector.c.ente, subq_sector.c.sector, subq_sector.c.total_usd).order_by(subq_sector.c.ente, desc(subq_sector.c.total_usd)):
        if row.ente not in top_sectores_dict:
            top_sectores_dict[row.ente] = []
        if len(top_sectores_dict[row.ente]) < 5:
            top_sectores_dict[row.ente].append({
                'sector': row.sector,
                'total_usd': row.total_usd
            })

    return [
        {"tipo_ente": tipo_ente, "ente": ente, "garantia_soberana": garantia_soberana, "total_usd": total_usd, "top_financiadores": top_financiadores_dict.get(ente, []), "top_sectores": top_sectores_dict.get(ente, [])}
        for tipo_ente, ente, garantia_soberana, total_usd in resultados
    ]
