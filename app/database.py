# app/database.py
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

writer_engine = create_async_engine(
    settings.writer_url(),
    future=True,
    pool_pre_ping=True,
    echo=False,
)
reader_engine = create_async_engine(
    settings.reader_url(),
    future=True,
    pool_pre_ping=True,
    echo=False,
)

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
        yield session


# legacy alias for any old imports
engine = writer_engine