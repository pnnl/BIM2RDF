


def groups():
    from pathlib import Path
    dir = Path(__file__).parent
    for i in dir.iterdir():
        if i.is_file():
            if i.suffix == '.ttl':
                yield i.stem.lower(), i
        else:
            for ii in i.iterdir():
                if ii.suffix == '.ttl':
                    yield i.stem.lower(), ii

names = frozenset(n for n, _ in groups())

from phantom.base import Phantom
def is_name(nm: str) -> bool: return nm in names
class Name(str, Phantom, predicate=is_name): ...

def get(name: str):
    assert(name in names)
    import rdflib
    g = rdflib.Graph()
    for n, f in groups(): g += rdflib.Graph().parse(f)
    if 'brick' in name.lower(): g = fix_brick(g)
    return g


def fix_brick(g):
    # https://github.com/BrickSchema/Brick/issues/308
    from rdflib import OWL as owl
    from rdflib import RDF as rdf
    from rdflib import URIRef
    v=URIRef('https://brickschema.org/schema/Brick#value')
    #g.remove( (v, rdf.type, owl.DatatypeProperty) )
    g.remove( (v, rdf.type, owl.ObjectProperty) )
    return g


def init():
    from .get import dl_brick
    dl_brick()
