import os

IS_DEV=os.environ.get("IS_DEV", "") in ("1", "True", "true")
DATABASE_URL=os.environ.get("DATABASE_URL")

FRONTEND_DOMAIN=os.environ.get("FRONTEND_DOMAIN")

LIMIT_TO_STATE = "Colorado"
