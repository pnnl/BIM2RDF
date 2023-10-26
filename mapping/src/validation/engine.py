from engine.triples import (
        Engine as _Engine, Result,
        Triples,
        OxiGraph)

from .shacl import shacl
from mapping.conversions import og2rg, rg2og
from ontologies import get


from functools import lru_cache
@lru_cache(1)
def ontology():
    _ = get('s223')
    from rdflib import Graph
    g = Graph()
    g.parse(_)
    return g


def _shacl_validation(db: OxiGraph):
    from mapping.engine import get_applicable
    _ = get_applicable(db._store)
    _ = og2rg(_)
    o = ontology()
    _ = shacl(_, namespaces=o.namespaces(), shacl=o,
              ontology=None, advanced=False, )
    return _


def shacl_validation(db: OxiGraph,) -> Triples:
    _ = _shacl_validation(db)
    _ = _.validation.report
    _ = rg2og(_)
    _ = Triples((q.triple for q in _))
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
        _.insert(self.db)
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
            assert(conforms == 'false' )
            conforms = False
        logger.info(f"conforms: {conforms}")
        assert(isinstance(conforms, bool))
        return Result(_, conforms)
    
    def __call__(self) -> Result:
        _ = super().__call__()
        v = self.validate()
        return v

