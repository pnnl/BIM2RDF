
def test():
    import rules.rules as r
    #sg = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    #_ = ''
    #_ = tuple(sg(_))
    #breakpoint()
    sg = r.SpeckleGetter.from_names(project='test', model='pritoni 1.ifc')
    #breakpoint()
    #d = tuple(r.data(_))
    #print(len(d))
    #assert(d)
    from rdf_engine import Engine
    db = Engine([sg], derand=False, MAX_NCYCLES=1, ).run()
    assert(len(db))
    from pyoxigraph import RdfFormat
    db.dump('db.ttl', format=RdfFormat.N_QUADS)
    #sensor-room mapping rule


if __name__ ==  '__main__':
    test()