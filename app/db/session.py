from app.core.settings import settings

# DB 관련
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)