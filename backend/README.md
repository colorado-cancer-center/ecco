# COCancerScope Backend

This folder contains the implementation of a RESTful API for the project. The
API itself is implemented in [FastAPI](https://fastapi.tiangolo.com/), and we
use [SQLModel](https://sqlmodel.tiangolo.com/) for describing the database
schema and interacting with the database. We use
[Alembic](https://alembic.sqlalchemy.org/en/latest/) for managing schema
migrations.


## Populating an Empty Database

Typically ECCO is distributed with a database dump, but if you want
to start over from scratch you can first dump the database by running:

```shell
./run_stack.sh down -v # brings the stack down and purges all volumes
./run_stack.sh         # brings the stack back up so we can import new data
```

Then run the following series of commands within the `backend` container:

```shell
./commands/add_us_states.py 
./commands/import_cif_data.py <CIF data folder>
./commands/import_scp_data.py <SCP data folder>
./commands/import_cancer_disparities.py <Disparities Excel Sheet>
./commands/import_radon.py <Radon Excel Sheet>
./commands/import_locations.py <Location Category JSON> <Location Data JSON>
./commands/import_hpv.py <Sheet 1> [Sheet 2...]
./commands/import_vaping_data.py
./commands/import_ccc_state_stats.py <State Stats Excel Sheet>
```

The geometry tables `County` and `Tract` are populated
via `start_app.sh` every time the `backend` container starts.

(NOTE: Manually importing the data as described above will be replaced with a
proper data import pipeline in the near future.)


## Performing Schema Migrations

First, you should be in the `./backend/app` folder, and ideally inside the
container which is running the backend, if you're using Docker Compose.

After modifying the  models in `./backed/app/models/`, you'll need to generate a
migration, i.e. a set of database operations (adding tables, modifying columns,
etc.) that move us from the previous version of the models to the new one.

To automatically generate a migration, run the following:

```shell
alembic revision --autogenerate -m "<brief description here>"
```

This will inspect the current database and the model files, then create a
best-effort guess at a migration to bring the database up-to-date, which it will
put in `./backend/app/migrations/versions` with a name derived from your
description. Don't be afraid to read and/or modify the migration! Alembic's
autogenerate feature generally does a good job, but it doesn't get everything
right.

Once you've inspected the new migration and you're happy with it, you can apply
it to your current database with the following command:

```shell
alembic upgrade head
```

If all goes well, your database will be upgraded in-place to the new schema;
you'll see a line like `Running upgrade <old revision> -> <new revision>, <your
description here>` in the output, one per migration you introduced. If for some
reason all doesn't go well, you can edit the migration file and try again. If
you find that you need to revert to a previous schema version, you can use the
following commands:

```shell
# shows the chain of migrations in reverse chronological order
# you'll need to run this to see the hashes of the migrations so far
alembic history
# downgrades to the specified revision
alembic downgrade <revision>
```

You can then reapply individual migrations via `alembic upgrade <revision>` or
go all the way back up to the current version using `alembic upgrade head`.

### Side Note: Data Migrations

Alembic autogenerate also doesn't capture data migrations (i.e. anything that
involves changing the contents of tables), but Alembic migrations are capable of
performing data migrations, too.

Say that you introduced a table of US states that's intended to always be
populated with the 50 US states: Alembic autogenerate would create the table,
but it wouldn't populate it. You can instead edit the migration and add your
data insertion statements after the table creation statements.  You'd typically
use this approach for "fixture" data, i.e. things like references or fixed
options that you need to reference from another table.
