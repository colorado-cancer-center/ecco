from contextlib import contextmanager
import os

from typing import AsyncGenerator, Generator

from settings import DATABASE_URL

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


DB_ECHO_USAGE = os.environ.get("DB_ECHO_USAGE", False)

# we disable pooling via poolclass=NullPool to prevent tests from crashing with
# 'attached to a different loop', even though it appears to work fine in actual
# use.
# see here for more information:
# https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops
# FIXME: see if disabling pooling impacts performance, and perhaps only
#  disable it when running tests.
engine = create_async_engine(
    DATABASE_URL, echo=DB_ECHO_USAGE,
    poolclass=NullPool,
)

async def init_db():
    """
    Creates tables in the database via SQLModel's metadata.

    Currently unused, as we're using Alembic for schema migrations,
    including the initial table creation.
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

sync_engine = create_engine(
    DATABASE_URL.replace("asyncpg", "psycopg2"), echo=DB_ECHO_USAGE
)

@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """
    Gets a synchronous db session, for use when we don't
    have an async context available.
    """
    sync_session = sessionmaker(
        sync_engine, class_=Session, expire_on_commit=False
    )
    with sync_session() as session:
        yield session
