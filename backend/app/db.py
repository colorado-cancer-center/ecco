import os

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from settings import DATABASE_URL

DB_ECHO_USAGE = os.environ.get("DB_ECHO_USAGE", False)

# when running tests, the test harness tries to create its own loop which then
# interferes with the loop that FastAPI creates.
#
# setting poolclass=NullPool resolves this by not sharing the connection between
# the two loops, but it may have performance implications. we may consider only
# disabling pooling during tests.
#
# see the following for more details:
# https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops

engine = create_async_engine(
    DATABASE_URL, echo=DB_ECHO_USAGE,
    poolclass=NullPool,
)

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
