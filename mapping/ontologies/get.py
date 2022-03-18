import rdflib
from pathlib import Path
onto_loc = Path(__file__).parent


def get_223p() -> rdflib.Graph:
    g = rdflib.Graph()
    for f in (f for f in ( onto_loc / 'reference-223p').iterdir() if f.suffix == '.ttl'):
        g += rdflib.Graph().parse(f)
    return g


def get_brick() -> rdflib.Graph:
    dst = onto_loc / 'Brick.ttl'
    src = 'https://brickschema.org/schema/Brick'
    if not dst.exists():
        from urllib.request import urlretrieve
        urlretrieve(src, dst)
    return rdflib.Graph().parse(dst)

