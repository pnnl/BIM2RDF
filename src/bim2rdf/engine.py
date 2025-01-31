# do i need this module to specify something?
# rdf-engine program?
class Run:
    class defaults:
        from pathlib import Path
        from mapping import dir as mapdir
        mapdirs = [ mapdir / 'test' ]
        MAX_NCYCLES = 10
        del Path

    from pyoxigraph import Store
    def __init__(self, db=Store()):
        self.db = db
    from pathlib import Path
    @classmethod
    def from_path(cls, pth: Path|str, clear=True):
        if isinstance(pth, str): pth = cls.Path(pth)
        if clear:
            if pth.exists():
                from shutil import rmtree
                rmtree(pth)
        return cls(cls.Store(str(pth)))

    def run(self, *,
            ontology:       Path,
            project_name:   str,
            model_name:     str,  # TODO: nameS
            map_dirs = defaults.mapdirs,
            MAX_NCYCLES=defaults.MAX_NCYCLES,
            log=True,
            ):
        db = self.db
        import rules as r
        sg = r.SpeckleGetter.from_names(project=project_name, model=model_name)
        # gl https://raw.githubusercontent.com/open223/defs.open223.info/0a70c244f7250734cc1fd59742ab9e069919a3d8/ontologies/223p.ttl
        # https://github.com/open223/defs.open223.info/blob/4a6dd3a2c7b2a7dfc852ebe71887ebff483357b0/ontologies/223p.ttl
        on = r.ttlLoader(ontology)
        from rdf_engine import Engine, logger
        if log:
            import logging
            logging.basicConfig(force=True) # force removes other loggers that got picked up.
            logger.setLevel(logging.INFO)
        db = Engine([sg, on], db=db, derand=False, MAX_NCYCLES=1, log_print=True ).run()

        def m():
            for d in map_dirs:
                d = self.Path(d)
                assert(d.exists())
                yield from d.glob('**/*.rq')
        m = [r.ConstructQuery.from_path(p)
             for p in m()]
        # TODO: file this under 'rules/tq'?
        dq = """
        prefix q: <urn:meta:bim2rdf:ConstructQuery:>
        construct {?s ?p ?o.}
        WHERE {
        <<?s ?p ?o>> q:name ?mo.
        filter (CONTAINS(?mo, ".mapping.") || CONTAINS(?mo, ".data.") ) 
        }"""
        # TODO: file this under 'rules/ttl'?
        sq = """
        prefix ttl: <urn:meta:bim2rdf:ttlLoader:>
        construct {?s ?p ?o.}
        WHERE {
        <<?s ?p ?o>> ttl:source ?mo.
        filter (CONTAINS(?mo, "223p.ttl") )
        }
        """
        tq = r.TopQuadrantInference(data=dq, shapes=sq)
        return Engine(m+[tq],
                      db=db,
                      MAX_NCYCLES=MAX_NCYCLES,
                      derand='canonicalize',
                      log_print=True ).run()

