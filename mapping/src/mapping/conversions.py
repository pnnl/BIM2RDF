from rdflib import Graph
from pyoxigraph import Store


def og2rg(og: Store,) -> Graph:
    from io import BytesIO
    _ = BytesIO()
    to = 'text/turtle'
    og.dump(_, to)
    _.seek(0)
    _ = Graph().parse(_, to)
    return _


from io import BytesIO
def rg2og(r: Graph) -> Store:
    to = 'text/turtle'
    _ = BytesIO()
    r.serialize(_, to)
    from pyoxigraph import Store
    _.seek(0)
    r: Store = Store()
    r.load(_, to) # where illegal rdf with literal subjects is an issue
    return r

