
# annotates models with metadata (at the moment, just __skip_autogenerate__).
# models that inherit from this mixin can set __skip_autogenerate__=True
# to cause alembic to skip them when autogenerating migrations.
# (this skipping is implemented in our alembic env.py file)
# adapted from https://stackoverflow.com/a/62053332/22216869

class ModelInfoMetaMixin(object):
    def __init__(cls, *args, **kwargs):
        skip_autogenerate = cls.__dict__.pop("__skip_autogenerate__", None)

        super(ModelInfoMetaMixin, cls).__init__(*args, **kwargs)

        if skip_autogenerate is not None and getattr(cls, "__table__", None) is not None:
            cls.__table__.info["skip_autogenerate"] = skip_autogenerate
