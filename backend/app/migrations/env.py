import os
import asyncio
from json import loads
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
import geoalchemy2

from alembic import context

from settings import DATABASE_URL

# verify, but we may need to import all our models here(?)
from models import *

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

exclude_tables = os.getenv("DB_EXCLUDE_TABLES", "").split(",")

def filter_db_objects( object, name, type_, *args, **kwargs ):
   # print(f"Checking object {object}: ", type(object), type(name), type_)

   if type_ == "table":
       return name not in exclude_tables and not "spatial_ref_sys" in name and not object.info.get("skip_autogenerate", False)
   if type_ == "index" and name.startswith("idx") and name.endswith("geom"):
       return False

   return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=filter_db_objects
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=filter_db_objects
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # connectable = async_engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    DB_ECHO_ALEMBIC = os.environ.get("DB_ECHO_ALEMBIC", False)

    connectable = create_async_engine(DATABASE_URL, echo=DB_ECHO_ALEMBIC, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
