from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Engines
writer_engine = create_async_engine(
    settings.writer_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args={"ssl": True},  # RDS SSL 강제 시 사용
)
reader_engine = create_async_engine(
    settings.reader_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args={"ssl": True},
)

# SessionMakers
WriterSessionLocal = sessionmaker(writer_engine, class_=AsyncSession, expire_on_commit=False)
ReaderSessionLocal = sessionmaker(reader_engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_writer_db():
    async with WriterSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_reader_db():
    async with ReaderSessionLocal() as session:
        # read-only path; still returns a snapshot
        yield session


# Legacy alias (optional): allow old code importing `engine`
engine = writer_engine