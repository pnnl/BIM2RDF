"""
programmatic generation of queries
"""
from ..engine import Triples, PyRule, ConstructRule as _ConstructRule, OxiGraph

# these could come from ontology.
parts = {
    's223': "standard223",
    'rdfs': "rdf-schema",
    'rdf': '22-rdf-syntax-ns',
    'qudt': 'qudt',
    'shacl': 'shacl',
    }


from functools import lru_cache
@lru_cache
def namespaces():
    from ontologies import namespace
    def o():
        from ontologies import namespaces
        for nss in namespaces():
            if 'imported' in str(nss.path):
                for pfx, ns in nss.namespaces():
                    yield namespace(pfx, ns)
    def s():
        from speckle import namespaces
        return namespaces()
    return tuple(o())+tuple(s())


def make_regex_parts(parts):
    for part in parts:
        for po in ('p', 'o'):
            #       uri cast as string so that regex can be applied
            yield f"""regex(str(?{po}), "{part}")"""


def sample_data():
    # to trigger metadata creation
    import pyoxigraph as g
    _ = [g.Triple(g.BlankNode(), g.NamedNode('urn:predicate'), g.BlankNode())]
    return _

def mkttl(triples): # could use pyoxigraph serialize/deserialize but overkill
    _ = triples
    _ = map(lambda t: f"{t}.", _)
    _ = '\n'.join(_)
    return _

def sample_pyfunc(db):
    _ = sample_data()
    return Triples(_)
sample_pyrule_data = PyRule(sample_pyfunc)(OxiGraph())

def sample_constructquery():
    _ = sample_data()
    _ = mkttl(_)
    _  = f"construct {{{_}}} where {{}}"
    return _

class ConstructRule(_ConstructRule):
    def __init__(self, cq: 'ConstructQuery') -> None:
        self._spec = cq
    @property
    def path(self):
        from pathlib import Path
        return Path('.') / self.name
    @property
    def name(self): return 'sample.rq'
sample_constructrule_data = ConstructRule(sample_constructquery())(OxiGraph())


def sample_constructrule_meta():
    _ = sample_constructrule_data
    return get_meta(_)
def sample_pyrule_meta():
    _ = sample_pyrule_data
    return get_meta(_)

def get_meta(triples):
    """<<?s ?p ?o>>  ?m <<?ms ?mp ?mo>>."""
    from pyoxigraph import Triple
    from types import SimpleNamespace as NS
    for s,p,o in triples:
        if isinstance(s, Triple):
            assert(isinstance(o, Triple))
            yield NS(m=p, ms=o.subject, mp=o.predicate, mo=o.object)


class QueryRuleType:
    from typing import Literal
    def __init__(self,
            rule_type: Literal['constructrule'] | Literal['pyrule'],):
            #specific: Literal['mapping'] | Literal['ontology'] | None = None ) -> None:
        # allowable combos
        assert(rule_type in {'constructrule', 'pyrule'})
        self.rule_type = rule_type
        return
        if rule_type == 'construct' and specific:
            assert(specific in {'mapping'} )
        if rule_type == 'pyrule' and specific:
            assert(specific in {'ontology'})
        self.specific = specific
    
    def __str__(self) -> str:
        return f"{self.rule_type}"#+f"{'.'+self.specific if self.specific else ''}"
    
    def __eq__(self, other) -> bool:
        return str(self) == str(other)
    
    def pattern(self):
        if self.rule_type == 'constructrule':
            _ = sample_constructrule_meta
        else:
            assert(self.rule_type == 'pyrule')
            _ = sample_pyrule_meta
        _ = next(_()) # just take one. good enough?
        return f"<<?s ?p ?o>> {_.m} <<{_.ms} {_.mp} ?mo>>." # ?mo is variable


class Queries:

    def query_template(self, pattern, filter):
        assert('filter' in filter)
        _ = f"""
        construct {{?s ?p ?o }}
        where {{
        ?s ?p ?o.
        {pattern}
        {filter}
        }}
        """
        return _
    
    #from ..engine import ConstructQuery, PyRuleCallable
    def querymaker(self, rule_arg, *p, **k,):
        if callable(rule_arg): #isinstance(rule_arg, pyrulecallable): # assume this is pyrulecallable
            from ..engine import PyRule
            rule = PyRule(rule_arg, *p, **k)
        else:
            assert(isinstance(rule_arg, str)) # constructrule
            from ..engine import ConstructRule
            rule = ConstructRule(rule_arg, *p, **k)
        from types import SimpleNamespace as NS
        # 'defaults'
        return NS(
        pattern = QueryRuleType(rule.__class__.__name__.lower()).pattern(),
        filter =  f'filter contains(?mo, "{rule.name}")',
        maker = lambda pattern, filter: self.query_template(pattern, filter))

    def _union(self):
        # idk if it's uself to combine the queries.
        _ = f"""
        construct {{?s ?p ?o }}
        where {{
        ?s ?p ?o.
        {{{full_ontology_pattern}}}
        union
        {{{mapped_pattern}}}
        }}
        """
        # or could say NOT speckle.
        # or filter FOR the 
        # FILTER({' || '.join(make_regex_parts(parts.values())) } )
        return _
    
class queries:
    """queries relevant to project"""
    def __init__(self) -> None:
        self.q = Queries()

    @property
    def mapped(self):
        pattern = QueryRuleType('constructrule').pattern()
        filter = f'filter contains(?mo, ".mapping." )'
        _ = self.q.query_template(pattern, filter)
        return _
    
    @property
    def ontology(self,):
        from ..speckle import get_ontology
        _ = self.q.querymaker(get_ontology)
        return _.maker(_.pattern, _.filter)
    
    @property
    def speckle(self):
        from ..speckle import get_speckle
        _ = self.q.querymaker(get_speckle)
        return _.maker(_.pattern, _.filter)
    
    @property
    def shacl(self):
        from validation.engine import shacl_validation
        _ = self.q.querymaker(shacl_validation)
        return _.maker(_.pattern, _.filter)

queries = queries()


if __name__ == '__main__':
    import fire
    fire.Fire(queries)