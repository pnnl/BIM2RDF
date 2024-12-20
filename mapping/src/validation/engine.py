from engine.triples import (
        Engine as _Engine, Result,
        Triples,
        OxiGraph)


def _shacl_validation(db: OxiGraph):
    _ = db._store
    from mapping.engine import select
    from mapping.utils.queries import queries
    _ = select(_,
            (queries.rules.mapped,
             queries.rules.shacl_inferred,
             queries.rules.rdfs_inferred,))
    from mapping.conversions import og2rg
    _ = og2rg(_)
    from mapping.utils.rdflibgraph import copy
    _ = copy(_)
    from ontologies import get
    from ontologies.collect import collect
    o = collect(
            {'validation/',
            '~validation/schema', # this is ontology 'self' validation. don't need this.
            'models/',
            'vocab/' # 
            }  )
    # from rdflib import Graph
    # o = Graph()
    # o.parse(get('defs'))
    for t in o: _.add(t)
    from .shacl import shacl
    from mapping.utils.queries import namespaces
    _ = shacl(_, namespaces=namespaces(),
              shacl=o,
              advanced=False, )
    return _


def shacl_validation(db: OxiGraph,) -> Triples:
    _ = _shacl_validation(db)
    _ = _.validation.report
    from mapping.utils.conversions import rg2triples
    _ = rg2triples(_)
    return _


def shapes():
    from project import root
    shapes = root / 'models' / 'artifacts' / 'ontology.ttl'
    from mapping.utils.data import get_data
    return get_data(shapes)

def shacl_validation(db: OxiGraph,
                     shapes = shapes,
                     ) -> Triples:
    s = db._store
    from mapping.utils.queries import queries
    from mapping.utils.queries import select
    _ = select(s, (
            queries.rules.mapped,
            queries.rules.rdfs_inferred,
            queries.rules.shacl_inferred,
            ) ) #
    shapes = shapes()
    from itertools import chain
    _ = chain(_, shapes)
    from validation.shacl import tqshacl
    _ = tqshacl('validate', _,)
    return _



import logging
logger = logging.getLogger('validation')

class Engine(_Engine):

    def validate(self) -> Result:
        from mapping.engine import PyRule
        logger.info('validating...')
        # one-time 'rule'
        _ = PyRule(shacl_validation)
        _ = _(self.db)
        from pyoxigraph import Quad
        self._db._store.bulk_extend(Quad(*t) for t in _)
        from mapping.utils.queries import namespaces
        sh = {p:ns for p,ns in  namespaces()}
        sh = sh['sh']
        q = f"""
        prefix sh: <{sh}>
        select ?conforms where {{
            ?_v sh:conforms ?conforms.
        }}
        """
        _ = self._db._store.query(q)
        _ = list(_)
        assert(len(_) == 1)
        conforms = _[0][0].value
        if conforms == 'true':
            conforms = True
        else:
            assert(conforms == 'false')
            conforms = False
        logger.info(f"conforms: {conforms}")
        assert(isinstance(conforms, bool))
        return Result(self.db, conforms)
    
    def __call__(self) -> Result:
        _ = super().__call__()
        v = self.validate()
        return v

