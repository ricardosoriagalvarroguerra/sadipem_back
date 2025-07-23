from sqlalchemy import Column, Text, Float
from database import Base

class DatosSadipem(Base):
    __tablename__ = "datos_sadipem"

    tipo_ente = Column(Text)
    uf = Column(Text)
    ente = Column(Text)
    id = Column(Text, primary_key=True, index=True)
    tipo_registro = Column(Text)
    tipo_deuda = Column(Text)
    RGF_clasificacion = Column(Text)
    tipo_acreedor = Column(Text)
    nombre_acreedor = Column(Text)
    fecha_contratacion = Column(Text)
    divisa_contratacion = Column(Text)
    valor = Column(Text)
    descripcion = Column(Text)
    estado = Column(Text)
    garantia_soberana = Column(Text)
    aprobacion_legislativa = Column(Text)
    fecha_finalizacion = Column(Text)
    value_num = Column(Float)
    tiempo_prestamo = Column(Float)
    descripcion_en = Column(Text)
    tc = Column(Float)
    valor_usd = Column(Float)
    sector = Column(Text)
    região = Column(Text)
