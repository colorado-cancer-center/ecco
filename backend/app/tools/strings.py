import os
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

# from sanitize-filename, but i decided against taking a dep on the package
# https://gitlab.com/jplusplus/sanitize-filename/-/raw/master/sanitize_filename/sanitize_filename.py?ref_type=heads
def sanitize(filename):
    """Return a fairly safe version of the filename.

    We don't limit ourselves to ascii, because we want to keep municipality
    names, etc, but we do want to get rid of anything potentially harmful,
    and make sure we do not exceed Windows filename length limits.
    Hence a less safe blacklist, rather than a whitelist.

    (From https://gitlab.com/jplusplus/sanitize-filename)
    """
    blacklist = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "\0"]
    reserved = [
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9",
    ]  # Reserved words on Windows
    filename = "".join(c for c in filename if c not in blacklist)
    # Remove all charcters below code point 32
    filename = "".join(c for c in filename if 31 < ord(c))
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.rstrip(". ")  # Windows does not allow these at end
    filename = filename.strip()
    if all([x == "." for x in filename]):
        filename = "__" + filename
    if filename in reserved:
        filename = "__" + filename
    if len(filename) == 0:
        filename = "__"
    if len(filename) > 255:
        parts = re.split(r"/|\\", filename)[-1].split(".")
        if len(parts) > 1:
            ext = "." + parts.pop()
            filename = filename[:-len(ext)]
        else:
            ext = ""
        if filename == "":
            filename = "__"
        if len(ext) > 254:
            ext = ext[254:]
        maxl = 255 - len(ext)
        filename = filename[:maxl]
        filename = filename + ext
        # Re-check last character (if there was no extension)
        filename = filename.rstrip(". ")
        if len(filename) == 0:
            filename = "__"
    return filename
