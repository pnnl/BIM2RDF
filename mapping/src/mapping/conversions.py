

from pyoxigraph import Store
def unstar(og: Store, quote=True):
    # quote and deal w/ isinstance(q.object, Triple)
    # for the general case
    from pyoxigraph import Store, Triple, Quad
    _ = Store()
    for q in og:
        if isinstance(q.subject, Triple):
            _.add(
                Quad(
                    q.subject.subject,
                    q.subject.predicate,
                    q.subject.object,
                    q.graph_name)
            )
        # dont care too much about inferencing metadata
        # the metadata are objects.
        #if isinstance(q.object, Triple):
        else:
            _.add(q)
    return _


from rdflib import Graph
def og2rg(og: Store, unstar_=True) -> Graph:
    from oxrdflib import OxigraphStore
    if unstar_: og = unstar(og)
    from rdflib import ConjunctiveGraph
    _ = OxigraphStore(store=og)
    # https://github.com/oxigraph/oxrdflib/issues/22#issuecomment-1499547525
    _ = ConjunctiveGraph(_)
    return _
    # below incurs copying and serialization costs
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
        # dont care too much about inferencing metadata
        # the metadata are objects.
        #if isinstance(q.object, Triple): 

        else:
            un_star.add(q)
    # can just oxigraph backend?
    un_star.dump(_, to)
    _.seek(0)
    _ = Graph().parse(_, to)
    return _


from io import BytesIO
def rg2og(r: Graph) -> Store:
    from oxrdflib import OxigraphStore
    if isinstance(r.store, OxigraphStore):
        return r.store._store
    to = 'text/turtle'
    _ = BytesIO()
    r.serialize(_, to)
    from pyoxigraph import Store
    _.seek(0)
    r: Store = Store()
    r.load(_, to) # where illegal rdf with literal subjects is an issue
    return r



from engine.triples import Triples
def rg2triples(r: Graph) -> Triples:
    to = 'text/turtle'
    from io import BytesIO
    _ = BytesIO()
    ## should blank node regen be addressed here...
    #  ... with a r.skolemize()?
    r.serialize(_, to)  
    _.seek(0)
    from pyoxigraph import parse
    _ = parse(_, to)
    _ = (t for t in _)
    return _
