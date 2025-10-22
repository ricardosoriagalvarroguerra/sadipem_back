import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import SQLALCHEMY_DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _ensure_indexes() -> None:
    """Create the indexes that keep the most common filters fast."""
    index_statements = (
        'CREATE INDEX IF NOT EXISTS idx_datos_sadipem_regiao ON datos_sadipem ("região")',
        'CREATE INDEX IF NOT EXISTS idx_datos_sadipem_sector ON datos_sadipem (sector)',
        'CREATE INDEX IF NOT EXISTS idx_datos_sadipem_tipo_deuda ON datos_sadipem (tipo_deuda)',
        'CREATE INDEX IF NOT EXISTS idx_datos_sadipem_year ON datos_sadipem ((substr(fecha_contratacion, 1, 4)))',
    )

    try:
        with engine.begin() as connection:
            for statement in index_statements:
                connection.execute(text(statement))
    except Exception as exc:  # pragma: no cover - defensive: prevents startup failure
        logger.warning("Could not ensure performance indexes exist: %s", exc)


_ensure_indexes()
