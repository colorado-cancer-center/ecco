import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

import db

# from tools.automap import automap ; await automap()

def as_dict(obj):
    data = obj.__dict__
    data.pop('_sa_instance_state')
    return data

async def automap():
    def reflect(conn):
        Base = automap_base()
        Base.prepare(conn, reflect=True)
        print(Base.classes.co_county_boundaries.__dict__)

    async with db.engine.begin() as conn:
        await conn.run_sync(reflect)
