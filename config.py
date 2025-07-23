# config.py
import os
from dotenv import load_dotenv

# Carga tu .env local (solo para desarrollo)
load_dotenv()

# Primero intenta leer DATABASE_URL (Railway la inyecta en producción)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Fallback a tu configuración local si no existe DATABASE_URL
    POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT     = os.getenv("POSTGRES_PORT", "5433")
    POSTGRES_DB       = os.getenv("POSTGRES_DB", "brasil")
    POSTGRES_USER     = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "rsgg2025")

    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://"
        f"{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/"
        f"{POSTGRES_DB}"
    )

# Opcional: levanta error si no hay URL en ningún lado
if not SQLALCHEMY_DATABASE_URL:
    raise RuntimeError("Ninguna configuración de base de datos encontrada en DATABASE_URL ni en variables locales")

# Ahora tu database.py sigue igual:
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
