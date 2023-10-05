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
    _ = get('223p')
    from rdflib import Graph
    g = Graph()
    g.parse(_)
    return g


def _shacl_validation(db: OxiGraph):
    from mapping.engine import get_filtered
    _ = get_filtered(db._store)
    #_ = OxiGraph()._store #gets stuck  here?!
    _ = og2rg(_)
    o = ontology()
    #_ = shacl(_, shacl=None, mangling happens, so just taking it direcly from ontology
    _ = shacl(_, namespaces=o.namespaces(), shacl=o,
              ontology=None, advanced=False, )
    return _

def shacl_validation(db: OxiGraph) -> Triples:
    _ = _shacl_validation(db)
    _ = _.validation.report
    #for t in _: ss.add(t)
    _ = rg2og(_)
    _ = Triples((q.triple for q in _))
    return _

import logging
logger = logging.getLogger('validation')

class Engine(_Engine):

    def validate(self) -> Result:
        logger.info('validating...')
        _ = _shacl_validation(self.db)
        conforms = _.validation.conforms
        assert(isinstance(conforms, bool))
        _ = _.validation.report
        _ = rg2og(_)
        _ = OxiGraph(_)
        return Result(_, conforms)
    
    def __call__(self) -> Result:
        _ = super().__call__()
        v = self.validate()
        for q in v.db._store: _.db._store.add(q)
        return _

