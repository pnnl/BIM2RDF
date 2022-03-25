import rdflib
from pathlib import Path
onto_loc = Path(__file__).parent


def dl_brick() -> rdflib.Graph:
    dst = onto_loc / 'Brick.ttl'
    src = 'https://brickschema.org/schema/Brick'
    if not dst.exists():
        from urllib.request import urlretrieve
        urlretrieve(src, dst)
    return rdflib.Graph().parse(dst)



