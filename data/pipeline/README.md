# ECCO Ingest Pipeline

This folder contains implementation for the ECCO ingest pipeline, which does the
following:

- pulls whatever the most up-to-date data is from a variety of sources:
    - places these downloaded data for the month into
      `/data/staging/<YYYY-mm-dd>/<source>`
    - formats this new data in a way that works with ECCO's existing import
      management commands
- loads the data from current staging folder into a fresh database:
    - creates a fresh database
    - bring up the backend, which runs migrations to set up the database
    - executes Django management command to import staging data into the
      database
    - dumps the new database release for the month into the `/db-exports` folder

Some files are updated either manually or on a longer-than-monthly cadence;
these files are stored in `/data/reference` and loaded by many of the management
commands.

The release acquisition pipeline relies on a few helper scripts for formatting
specific sources; you can find these under `/data/pipeline/scripts/`.


## Requirements

Similarly to running the app, you'll need
[Docker](https://docs.docker.com/get-started/get-docker/) installed. Nearly all
the work of acquiring a release and importing it into the database is done in
the backend API container, which includes all the dependencies for running the
pipeline.

We use [Snakemake](https://snakemake.readthedocs.io/en/stable/) to acquire new
release data; as mentioned above, this is placed under the `/data/staging/`
folder. Since Snakemake is included in the backend container, you don't need to
install it.

The acquisition of a release includes a step where addresses are geocoded to
coordinates; we rely on [Google's Geocoding
API](https://developers.google.com/maps/documentation/geocoding) for this. In
order to access the API, ensure that the `.env` file at the root of the repo has
a valid API key value for `MAPS_API_KEY`. See [Google's Geocoding API: Getting
Started](https://developers.google.com/maps/documentation/geocoding/cloud-setup)
guide for instructions.

The actual importing of the staging files into the database is facilitated by
Django management commands defined in the backend.


## Usage

To pull the latest data and format it, cd to `/data/pipeline` and run the script
`./produce_release.sh`; this will create a new folder under
`/data/staging/<YYYY-mm-dd>`, then create subdirectories and format the data
within each accordingly.

Once the staging data is created, the data will be loaded into the database.
Finally a database dump will be created in `/db-exports/ecco_<YYYY-mm-dd>.dump`.
Dumps are typically small (around ~11mb in size as of March 2025). Feel free to
check this file into source control so that anyone who clones ECCO will have the
most recent data.

When the stack is restarted, the db container will look for the most recent db
export in `/db-exports/` and load it automatically.

(The behavior of loading the most recent dump can be disabled by setting the env
var `SKIP_DB_LOAD=1`, just FYI.)
