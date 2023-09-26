import os

IS_DEV=os.environ.get("IS_DEV", "") in ("1", "True", "true")
DATABASE_URL=os.environ.get("DATABASE_URL")

LIMIT_TO_STATE = "Colorado"
