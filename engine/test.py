
def test():
    from engine.triples import (ConstructQuery,
                                 Rules, PyRule, noeffect_pyfunc, 
                                 Engine,
                                 Triples,
                                 OxiGraph)
    import pyoxigraph as g

    def _data(db: OxiGraph) -> Triples:
        _ = b'<http://example.com> <http://example.com/p> "1" .\n'
        _ = g.parse(_, 'text/turtle')
        _ = Triples(_)
        return _
    Data = PyRule(_data)
    _ = """
    construct {
        <http://example.com/a> <http://www.w3.org/2000/01/rdf-schelabel> "something" .}
    where {  }
    """
    Construct = ConstructQuery(_)
    rules = Rules([noeffect_pyfunc, Data, Construct])
    engine = Engine(rules, OxiGraph(g.Store()) )
    res = engine()
    _ = res.db
    _ = list(_)
    return _


def test_deanon():
    from engine.triples import deanon
    from pyoxigraph import Triple, NamedNode, BlankNode
    x = BlankNode('x')
    y = BlankNode('y')
    p = NamedNode('p:')
    t = Triple(x, p, y)
    m = NamedNode('m:')
    i = [
        Triple(t, m , t),
        t 
        ]
    o = deanon(i)
    o = list(o)
    assert(o[0].subject.subject     == o[1].subject  )
    assert(o[0].subject.object      == o[1].object  )
    assert(o[0].object.subject      == o[1].subject  )
    assert(o[0].object.object       == o[1].object  )
    assert(o[0].subject.predicate   == o[1].predicate  )
    assert(o[0].object.predicate    == o[1].predicate  )
