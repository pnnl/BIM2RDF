
def test():
    from pyoxigraph import Store
    from pathlib import Path
    if Path('db').exists():
        from shutil import rmtree
        rmtree('db',)
    db = Store('db')
    import rules as r
    sg = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    # https://raw.githubusercontent.com/open223/explore.open223.info/8c19f4e41692f223ef17eadb5ee1ac6e4edeb28a/ontologies/223p.ttl
    tl = r.ttlLoader(Path('223p.ttl'))
    from rdf_engine import Engine, logger
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    logger.setLevel(logging.INFO)
    db = Engine([sg, tl], db=db, derand=False, MAX_NCYCLES=1, log_print=True ).run()
    from pathlib import Path
    m = r.ConstructQuery.from_path( Path('../rules/test') / 'mapping' / 'luminaire.mapping.rq' )
    dq = """
    prefix q: <urn:meta:bim2rdf:ConstructQuery:>
    construct {?s ?p ?o.}
    WHERE {
    <<?s ?p ?o>> q:name ?mo.
    filter (CONTAINS(?mo, ".mapping.") || CONTAINS(?mo, ".data.") ) 
    }"""
    sq = """
    prefix ttl: <urn:meta:bim2rdf:ttlLoader:>
    construct {?s ?p ?o.}
    WHERE {
    <<?s ?p ?o>> ttl:source ?mo.
    filter (CONTAINS(?mo, "223p.ttl") ) 
    }
    """
    tq = r.TopQuadrant(data=dq, shapes=sq)
    db = Engine([m, tq], db=db, derand='canonicalize', log_print=True ).run()
    print(len(db))
    from pyoxigraph import RdfFormat
    db.dump('db.ttl', format=RdfFormat.N_QUADS)


def xtest():
    import rules as r
    tf = r.ttlLoader('test.ttl')
    tu = r.ttlLoader('https://raw.githubusercontent.com/sparkica/rdf-extension/refs/heads/master/test/com/google/refine/test/org/deri/reconcile/files/sample.ttl')
    from rdf_engine import Engine, logger
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    #import logging
    #logging.basicConfig(force=True) 
    logger.setLevel(logging.INFO)
    db = Engine([tf, tu], derand=False, MAX_NCYCLES=1, log_print=True ).run()
    from pyoxigraph import RdfFormat
    db.dump('db.ttl', format=RdfFormat.N_QUADS)


if __name__ ==  '__main__':
    test()
