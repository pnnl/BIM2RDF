class Run:
    class defaults:
        from pathlib import Path
        from bim2rdf_mapping.construct import default_dir as mapdir
        map_dirs = [ mapdir  ]
        map_substitutions = {}
        ttls = [Path('ontology.ttl')]
        model_names = [
            'architecture/hvac zones',
            'architecture/lighting devices',
            'architecture/rooms and lighting fixtures',
            'electrical/panels',
            'electrical/electrical connections',
                       ]
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

    from typing import Iterable
    def run(self, *,
            project_name:   str,
            project_id:     str="",
            model_names:    Iterable[str]   =defaults.model_names,
            model_versions: Iterable[str]   = [],
            ttls:           Iterable[Path]  =defaults.ttls,
            map_dirs:       Iterable[Path]  =defaults.map_dirs,
            map_substitutions: dict         =defaults.map_substitutions, # TODO
            MAX_NCYCLES:    int             =defaults.MAX_NCYCLES,
            log=True,
            ):
        from rdf_engine import Engine, logger
        def lg(phase):
            if log:
                import logging
                logging.basicConfig(force=True) # force removes other loggers that got picked up.
                logger.setLevel(logging.INFO)
                div = '========='
                l = f"{div}{phase.upper()}{div}"
                logger.info(l)
        
        if project_name and project_id:
            raise ValueError('use project_id OR project_name')
        import bim2rdf_speckle.data as sd
        if project_id:
            project = sd.Project(project_id)
        else:
            assert(project_name)
            _ = [p for p in sd.Project.s() if p.name == project_name]
            if (len(_) > 1):    raise ValueError('project name not unique')
            if (len(_) == 0):   raise ValueError('project name not found')
            assert(len(_) == 1)
            project = _[0]

        
        #####
        lg('[1/3] data loading')
        db = self.db
        import bim2rdf_rules as r
        model_names =    tuple(model_names)
        model_versions = tuple(model_versions)
        if model_names and model_versions:
            raise ValueError('use model names OR versions')
        if model_names:
            sgs = [r.SpeckleGetter.from_names(project=project.name, model=n) for n in model_names]
        else:
            assert(model_versions)
            sgs = [r.SpeckleGetter(project_id=project.id, version_id=v) for v in model_versions]
        # gl https://raw.githubusercontent.com/open223/defs.open223.info/0a70c244f7250734cc1fd59742ab9e069919a3d8/ontologies/223p.ttl
        # https://github.com/open223/defs.open223.info/blob/4a6dd3a2c7b2a7dfc852ebe71887ebff483357b0/ontologies/223p.ttl
        ttls = [r.ttlLoader(self.Path(ttl)) for ttl in ttls]
        # data loading phase.                          no need to cycle
        db = Engine(sgs+ttls, db=db, derand=False, MAX_NCYCLES=1, log_print=log).run()

        #######
        lg('[2/3] mapping and inferencing')
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
                      log_print=log).run()
        
        ######
        lg('[3/3] validation')


