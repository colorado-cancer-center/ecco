# Implementation Details

So far, this repo contains:
- a PostGIS database to provide the geometry and statistics
- a RESTful backend API, implemented in FastAPI
- a Vue 3 frontend that visualizes the statistics on a map

## Prerequisites

You should have [Docker Desktop](https://docs.docker.com/get-docker/) installed
for your OS. You'll also need Docker Compose, which comes bundled with newer
versions of Docker Desktop, but if not you can install it by following these
instructions: [Docker Compose
Installation](https://docs.docker.com/compose/install/).

## Setup and Usage

First, copy `.env.TEMPLATE` to a new file named `.env`. Open the file and supply
a random value for the `POSTGRES_PASSWORD` line.

Then, execute `./run_stack.sh`, which will build the stack and bring it up in
development mode. It can take a long time for the stack to come up initially,
since the database is populated on first launch, but future launches should be
quick.

Once everything has settled, browse to http://localhost:8001 to see the
frontend, and http://localhost:8000/docs to see the backend documentation.

To bring down the stack, press `Ctrl-c` in the window where you ran
`run_stack.sh`. The stack should exit at this point, but the database will be
preserved for the next time you run it, dramatically speeding up startup time.
