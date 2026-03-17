from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Lê a URL do banco da variável de ambiente.
# Se não existir, usa SQLite local (desenvolvimento).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# Configuração do engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite: precisa de check_same_thread para FastAPI
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Azure SQL ou outro banco: usa connection pool
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        pool_recycle=3600,
        pool_pre_ping=True
    )

# Fábrica de sessões — cada request usa uma sessão isolada
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os models
Base = declarative_base()


def get_db():
    """
    Dependency injection para FastAPI.
    Cria uma sessão de banco por request e fecha ao final,
    mesmo se acontecer um erro no meio.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()