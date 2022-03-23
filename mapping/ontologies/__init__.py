


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


def get(name: str):
    assert(name in names)
    import rdflib
    g = rdflib.Graph()
    for n, f in groups(): g += rdflib.Graph().parse(f)
    return g


def init():
    from .get import dl_brick
    dl_brick()
