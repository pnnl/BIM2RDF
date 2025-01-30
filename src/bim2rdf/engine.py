# do i need this module to specify something?
# rdf-engine program?

def run(): 
    # maybe use rdf-engine program to structure? 
    from pyoxigraph import Store
    from pathlib import Path
    if Path('db').exists():
        from shutil import rmtree
        rmtree('db',)
    db = Store('db')
    import rules as r
    sg = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    # gl https://raw.githubusercontent.com/open223/defs.open223.info/0a70c244f7250734cc1fd59742ab9e069919a3d8/ontologies/223p.ttl
    # https://github.com/open223/defs.open223.info/blob/4a6dd3a2c7b2a7dfc852ebe71887ebff483357b0/ontologies/223p.ttl
    tl = r.ttlLoader(Path('223p.ttl'))
    from rdf_engine import Engine, logger
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    logger.setLevel(logging.INFO)
    db = Engine([sg, tl], db=db, derand=False, MAX_NCYCLES=1, log_print=True ).run()
    from pathlib import Path
    from mapping import dir as mpdir
    mpdir = mpdir / 'test'
    m = [
        r.ConstructQuery.from_path( mpdir / 'luminaire.mapping.rq'),
        r.ConstructQuery.from_path( mpdir / 'room.mapping.rq'),
    ]
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
    tq = r.TopQuadrantInference(data=dq, shapes=sq)
    return Engine(m+[tq], db=db, derand='canonicalize', log_print=True ).run()


if __name__ == '__main__':
    run()
