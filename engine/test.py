
def test():
    from engine.triples import (ConstructQuery,
                                 Rules, PyRule, NoEffect, 
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
    rules = Rules([NoEffect, Data, Construct])
    engine = Engine(rules, OxiGraph(g.Store()) )
    res = engine()
    _ = res.db
    _ = list(_)
    return _



if __name__ == '__main__':
    test()
