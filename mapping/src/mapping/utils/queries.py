"""
programmatic generation of queries
"""
from ..engine import Triples, PyRule, ConstructRule as _ConstructRule, OxiGraph
from pyoxigraph import Store
def select(store: Store, construct_queries) -> Triples:
    _ = map(lambda q: store.query(q) , construct_queries )
    from itertools import chain
    _ = chain.from_iterable(_)
    _ = Triples(_)
    return _

from functools import lru_cache
@lru_cache
def namespaces(unique=True):
    from ontologies import namespace
    def o():
        from ontologies import namespaces
        for nss in namespaces():
            for pfx, ns in nss.namespaces():
                yield namespace(pfx, ns)
    def s():
        from speckle import namespaces
        return namespaces()
    def ms():
        from mapping.speckle import namespaces
        return namespaces()
    def e():
        from ..engine import namespaces
        return namespaces()
    def em():
        from engine.triples import PyRule
        return (namespace('meta', PyRule.meta_uri,) ,)
    _ = tuple(o())+tuple(s())+tuple(e())+tuple(em())+tuple(ms())
    _ = sorted(_, key=lambda ns: ns.prefix )
    _ = tuple(frozenset(_))
    if unique:
        _ = {p:n for p,n in _}
        _ = tuple(_.items())
    return _



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
sample_pyrule_data = frozenset(PyRule(sample_pyfunc)(OxiGraph()))

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
sample_constructrule_data = frozenset(ConstructRule(sample_constructquery())(OxiGraph()))


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


class RuleQueries:

    def query_template(self, pattern, filter):
        assert('filter' in filter)
        _ = f"""
        ?s ?p ?o.
        {pattern}
        {filter}
        """
        from .query import ConstructQuery
        _ = ConstructQuery(
            constructbody='?s ?p ?o',
            wherebody=_)
        return str(_)
    
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
    
class rulequeries:
    """queries relevant to project"""
    def __init__(self) -> None:
        self.q = RuleQueries()

    @property
    def mapped(self):
        pattern = QueryRuleType('constructrule').pattern()
        filter = f'filter contains(?mo, ".mapping." )'
        _ = self.q.query_template(pattern, filter)
        return _
    
    
    @property
    def speckle(self):
        from ..speckle import get_speckle
        _ = self.q.querymaker(get_speckle)
        return _.maker(_.pattern, _.filter)
    
    @property
    def shacl_validation(self):
        from validation.engine import shacl_validation
        _ = self.q.querymaker(shacl_validation)
        return _.maker(_.pattern, _.filter)

    @property
    def shacl_inferred(self):
        from ..engine import topquadrant_rules
        _ = self.q.querymaker(topquadrant_rules)
        return _.maker(_.pattern, _.filter)
    @property
    def rdfs_inferred(self):
        from ..engine import rdflib_rdfs
        _ = self.q.querymaker(rdflib_rdfs)
        return _.maker(_.pattern, _.filter)
    

class queries:
    rules = rulequeries()

    @property
    def shacl_report(self):
        from .query import Prefixes, Node, known_prefixes
        S = lambda n: Node('sh', n)
        vr = S('ValidationResult')
        fn = S('focusNode')
        rm = S('resultMessage')
        vl = S('value')
        rp = S('resultPath')
        ss = S('sourceShape')  
        sv = S('resultSeverity')
        sc = S('sourceConstraintComponent')
        _ = Prefixes(p for p in known_prefixes if 'shacl' in str(p.uri) )
        _ = str(_)
        _ = _ + f"""
        select  {fn.var} {rm.var} {vl.var} {rp.var} {sv.var} {ss.var} where {{
        {vr.var} a {vr}.
        optional {{{vr.var} {fn} {fn.var}}}.
        optional {{{vr.var} {rm} {rm.var}}}.
        optional {{{vr.var} {vl} {vl.var}}}.
        optional {{{vr.var} {rp} {rp.var}}}.
        optional {{{vr.var} {sv} {sv.var}}}.
        optional {{{vr.var} {ss} {ss.var}}}.
        }}
        """
        return _    
        
    
queries = queries()

if __name__ == '__main__':
    import fire
    fire.Fire(queries)

