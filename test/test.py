
def test():
    import rules as r
    #sg = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    #_ = ''
    #_ = tuple(sg(_))
    #breakpoint()
    
    sg = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    #breakpoint()
    #d = tuple(r.data(_))
    #print(len(d))
    #assert(d)
    from rdf_engine import Engine, logger
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    #import logging
    #logging.basicConfig(force=True) 
    logger.setLevel(logging.INFO)
    db = Engine([sg], derand=False, MAX_NCYCLES=1, log_print=True ).run()

    #from rules.construct import dir as cdir
    from pathlib import Path
    m = r.ConstructQuery.from_path( Path('../rules/test') / 'mapping' / 'luminaire.mapping.rq' )
    db = Engine([m], derand='canonicalize', log_print=True ).run()
    assert(len(db))
    from pyoxigraph import RdfFormat
    db.dump('db.ttl', format=RdfFormat.N_QUADS)
    #sensor-room mapping rule

def test():
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
