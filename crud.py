from sqlalchemy.orm import Session
from sqlalchemy import func, text
from collections import defaultdict
from models import DatosSadipem

def get_datos(db: Session, region: str = None, sector: str = None):
    year_col = func.substr(DatosSadipem.fecha_contratacion, 1, 4)
    query = db.query(DatosSadipem)
    # Filtro por año de fecha_contratacion entre 2018 y 2024
    query = query.filter(
        year_col >= "2018",
        year_col <= "2024"
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
    sql = text(
        """
        SELECT "região" AS region, sector, SUM(valor_usd) AS total_usd
        FROM datos_sadipem
        GROUP BY GROUPING SETS (("região"), (sector))
        """
    )

    results = db.execute(sql).all()

    total_por_region = []
    total_por_sector = []
    for region, sector, total in results:
        if region is not None:
            total_por_region.append({"region": region, "total_usd": total})
        elif sector is not None:
            total_por_sector.append({"sector": sector, "total_usd": total})

    return {
        "total_por_region": total_por_region,
        "total_por_sector": total_por_sector,
    }

def get_valores_por_ente(db: Session):
    year_col = func.substr(DatosSadipem.fecha_contratacion, 1, 4)
    common_filters = [
        DatosSadipem.garantia_soberana == 'Si',
        DatosSadipem.tiempo_prestamo > 14,
        year_col >= "2019",
        year_col <= "2024",
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


def get_interno_externo_por_sector(db: Session, year: int):
    year_col = func.substr(DatosSadipem.fecha_contratacion, 1, 4)
    str_year = str(year)
    resultados = (
        db.query(
            DatosSadipem.sector,
            DatosSadipem.tipo_deuda,
            func.sum(DatosSadipem.valor_usd).label('total_usd')
        )
        .filter(year_col == str_year)
        .group_by(DatosSadipem.sector, DatosSadipem.tipo_deuda)
        .all()
    )

    data = defaultdict(lambda: {'interno': 0, 'externo': 0})
    for sector, tipo_deuda, total in resultados:
        if tipo_deuda:
            tipo = 'interno' if tipo_deuda.lower().startswith('int') else 'externo'
            data[sector][tipo] = total

    return [
        {'sector': sector, 'interno': valores['interno'], 'externo': valores['externo']}
        for sector, valores in data.items()
    ]
