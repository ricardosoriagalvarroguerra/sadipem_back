from pydantic import BaseModel
from typing import Optional

class DatosSadipemSchema(BaseModel):
    tipo_ente: Optional[str]
    uf: Optional[str]
    ente: Optional[str]
    id: str
    tipo_registro: Optional[str]
    tipo_deuda: Optional[str]
    RGF_clasificacion: Optional[str]
    tipo_acreedor: Optional[str]
    nombre_acreedor: Optional[str]
    fecha_contratacion: Optional[str]
    divisa_contratacion: Optional[str]
    valor: Optional[str]
    descripcion: Optional[str]
    estado: Optional[str]
    garantia_soberana: Optional[str]
    aprobacion_legislativa: Optional[str]
    fecha_finalizacion: Optional[str]
    value_num: Optional[float]
    tiempo_prestamo: Optional[float]
    descripcion_en: Optional[str]
    tc: Optional[float]
    valor_usd: Optional[float]
    sector: Optional[str]
    região: Optional[str]

    class Config:
        orm_mode = True

class RegionResponse(BaseModel):
    regiones: list[str]

class SectorResponse(BaseModel):
    sectores: list[str]


class InternoExternoSectorSchema(BaseModel):
    sector: Optional[str]
    interno: float
    externo: float
