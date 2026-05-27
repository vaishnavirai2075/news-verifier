import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import get_settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

def get_engine():
    settings = get_settings()
    DATABASE_URL = settings.DATABASE_URL
    logger.info(f"Connecting to: {DATABASE_URL}")
    return create_async_engine(DATABASE_URL, echo=settings.DEBUG)

def get_session_factory():
    return sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False
    )

async def get_db():
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")