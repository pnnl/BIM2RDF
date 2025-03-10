class Run:
    class _defaults:
        @property
        def model_names(self):
            from .queries import DefaultSubstitutions
            return frozenset(t[1] for t in DefaultSubstitutions.models()); del DefaultSubstitutions
        model_versions = []
        @property
        def included_mappings(self):
            from bim2rdf_mapping.construct import included_dir
            _ = list(included_dir.glob('**'))
            _ = [_.relative_to(included_dir) for _ in _]
            _ = [_ for _ in _ if _.parts and not _.name.startswith('_') ]
            _ = [str(_.as_posix()) for _ in _]
            return _
        additional_mapping_paths = []
        @property
        def mapping_substitutions(self):
            from .queries import SPARQLQuery
            _ = SPARQLQuery.defaults.substitutions; del SPARQLQuery
            return _
        mapping_subs_overrides = {}
        @property
        def ttls(self):
            from pathlib import Path
            return [Path('ontology.ttl')]
        inference = True
        validation = True
        MAX_NCYCLES = 10
        log = True
    defaults = _defaults()

    from pyoxigraph import Store
    def __init__(self, db=Store()):
        self.db = db
    
    from pathlib import Path
    from typing import Iterable
    def run(self, *,
            project_name:               str,
            project_id:                 str="",
            model_names:                Iterable[str]       =defaults.model_names,
            model_versions:             Iterable[str]       =defaults.model_versions,
            ttls:                       Iterable[Path|str]  =defaults.ttls,
            included_mappings:          Iterable[str]       =defaults.included_mappings,
            additional_mapping_paths:   Iterable[Path]      =defaults.additional_mapping_paths,
            mapping_subsitutitions:     dict[str, str]      =defaults.mapping_substitutions,
            mapping_subs_overrides:     dict[str, str]      =defaults.mapping_subs_overrides,
            inference:                  bool                =defaults.inference,
            validation:                 bool                =defaults.validation,
            MAX_NCYCLES:                int                 =defaults.MAX_NCYCLES,
            log:                        bool                =defaults.log,
            )->Store:
        """
        """
        model_names =       tuple(model_names)
        model_versions =    tuple(model_versions)
        if not (model_names or model_versions):
            return self.Store()

        n_phases = 3 if validation else 2
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
        lg(f'[1/{n_phases}] data loading')
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
        lg(f'[2/{n_phases}] mapping and maybe inferencing')
        mapping_subsitutitions.update(mapping_subs_overrides)
        included_mappings = tuple(included_mappings)
        if included_mappings:
            from bim2rdf_mapping.construct import included_dir
            for _ in included_mappings: assert((included_dir / _).exists() )
            included_mappings = [(included_dir / _) for _ in included_mappings]
        else:
            included_mappings = []
        from pathlib import Path
        map_paths = tuple(included_mappings)+tuple(Path(p) for p in additional_mapping_paths)
        def unique_queries():
            from .queries import SPARQLQuery
            qs = SPARQLQuery.s((map_paths), substitutions=mapping_subsitutitions)
            from collections import defaultdict
            dd = defaultdict(list)
            for q in qs: dd[q.string].append(q)
            #      take the first
            return [q[0] for q in dd.values()]
        ms = [r.ConstructQuery(
                    q.string,
                    name=r.ConstructQuery.mk_name(q.source))
              for q in unique_queries()]
        
        from .queries import queries
        if inference:
            inf = [r.TopQuadrantInference(
                        data=queries['mapped'],
                        shapes=queries['ontology'])]
        else:
            inf = []
        _ = ['ontology' in str(t.source) for t in ttls if isinstance(t.source, Path) ]
        if sum(_) == 0:
            if inference:
                from warnings import warn
                warn('ontology.ttl not found')
                inf = []
        if sum(_) > 1:
            if inference:
                from warnings import warn
                warn('more than one ontology.ttl found')
        db = Engine(ms+inf,
                      db=db,
                      MAX_NCYCLES=MAX_NCYCLES,
                      #derand='canonicalize', # gets stuck! probably bc some bad interaction with inferencing
                      log_print=log).run()
        

        ######
        if validation:
            lg(f'[3/{n_phases}] validation')
            db = Engine([r.TopQuadrantValidation(
                                data=queries['mapped'],
                                shapes=queries['ontology'])],
                         db=db,
                         derand=False,
                         MAX_NCYCLES=1,  # just one
                         log_print=log,).run()
        return db




__all__ = ['Run']