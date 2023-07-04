from rdflib import Graph
from pyoxigraph import Store, Triple, Quad


def og2rg(og: Store,) -> Graph:
    from io import BytesIO
    _ = BytesIO()
    to = 'text/turtle'
    un_star = Store()
    for q in og:
        if isinstance(q.subject, Triple):
            un_star.add(
                Quad(
                    q.subject.subject,
                    q.subject.predicate,
                    q.subject.object,
                    q.graph_name)
            )
        else:
            un_star.add(q)
    un_star.dump(_, to)
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

