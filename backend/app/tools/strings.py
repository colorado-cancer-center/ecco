import re
import unicodedata

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def slug_modelname_sans_type(model, type):
    """
    Normalizes a model name by removing the type (county or tract) and
    slugifying the result.
    """
    return slugify(model.__name__.lower().replace(type, ""))
