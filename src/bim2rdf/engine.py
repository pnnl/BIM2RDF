class Run:
    class defaults:
        from .queries import DefaultSubstitutions
        model_names = frozenset(t[1] for t in DefaultSubstitutions.models()); del DefaultSubstitutions
        model_versions = []
        use_default_mappings = True
        from pathlib import Path
        additional_mapping_dirs = [  ]
        from .queries import SPARQLQuery
        map_substitutions = [SPARQLQuery.defaults.substitutions]; del SPARQLQuery
        ttls = [Path('ontology.ttl')]
        inference = True
        MAX_NCYCLES = 10
        del Path

    from pyoxigraph import Store
    def __init__(self, db=Store()):
        self.db = db
    
    from pathlib import Path
    from typing import Iterable
    def run(self, *,
            project_name:   str,
            project_id:     str="",
            model_names:    Iterable[str]       =defaults.model_names,
            model_versions: Iterable[str]       =defaults.model_versions,
            ttls:           Iterable[Path]      =defaults.ttls,
            use_default_mappings:bool           =defaults.use_default_mappings,
            additional_mapping_dirs:Iterable[Path]  =defaults.additional_mapping_dirs,
            map_substitutions: Iterable[dict]   =defaults.map_substitutions,
            inference                           =defaults.inference,
            MAX_NCYCLES:    int                 =defaults.MAX_NCYCLES,
            log=True,
            ):
        """
        map_substitutions is a list. later mappings will override earlier ones.
        """
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
        model_names =    frozenset(model_names)
        model_versions = frozenset(model_versions)
        if model_names and model_versions:
            raise ValueError('use model names OR versions')
        if model_names:
            sgs = [r.SpeckleGetter.from_names(project=project.name, model=n) for n in model_names]
        else:
            #assert(model_versions) to allow no models
            sgs = [r.SpeckleGetter(project_id=project.id, version_id=v) for v in model_versions]
        # gl https://raw.githubusercontent.com/open223/defs.open223.info/0a70c244f7250734cc1fd59742ab9e069919a3d8/ontologies/223p.ttl
        # https://github.com/open223/defs.open223.info/blob/4a6dd3a2c7b2a7dfc852ebe71887ebff483357b0/ontologies/223p.ttl
        ttls = [r.ttlLoader(self.Path(ttl)) for ttl in ttls]
        # data loading phase.                          no need to cycle
        db = Engine(sgs+ttls, db=db, derand=False, MAX_NCYCLES=1, log_print=log).run()

        #######
        lg('[2/3] mapping and maybe inferencing')
        from .queries import SPARQLQuery
        _ = {}
        for ms in map_substitutions: _.update(ms)
        substitutions = _
        if use_default_mappings:
            from bim2rdf_mapping.construct import default_dir as dmd
            map_dirs = [dmd]
        else:
            map_dirs = []
        map_dirs = tuple(additional_mapping_dirs)+tuple(map_dirs)
        def unique_queries():
            qs = SPARQLQuery.s((map_dirs), substitutions=substitutions)
            from collections import defaultdict
            dd = defaultdict(list)
            for q in qs: dd[q.string].append(q)
            #      take the first
            return [q[0] for q in dd.values()]
        ms = [r.ConstructQuery(
                    q.string,
                    name=r.ConstructQuery.mk_name(q.source))
              for q in unique_queries()]
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
        inf = [r.TopQuadrantInference(data=dq, shapes=sq)] if inference else []
        return Engine(ms+inf,
                      db=db,
                      MAX_NCYCLES=MAX_NCYCLES,
                      derand='canonicalize',
                      log_print=log).run()
        
        ######
        lg('[3/3] validation')

