"""
engine specialization
"""
from engine.triples import (
        ConstructQuery,
        Rules,
        Rule ,  # for owlrl TODO
        PyRule,
        Triples,
        Engine, OxiGraph)


from owlrl.CombinedClosure import RDFS_OWLRL_Semantics as Semantics

def rdflib_semantics(db: OxiGraph) -> Triples:
    from rdflib import  Graph
    #https://github.com/oxigraph/oxrdflib/blob/f0f0a110c58e8e82acd2eb0af5514392d2941596/oxrdflib/__init__.py#L20
    # store constructor deps on 'config'. should be able to just taks store
    #s._store = g._store
    # will need to copy b/c the rule iface is triples
    # rdflibg = Graph(s)
    from io import BytesIO
    _ = BytesIO()
    db._store.dump(_, 'text/turtle')
    _.seek(0)
    g1 = Graph().parse(_, 'text/turtle')
    # copy
    _.seek(0)
    g2 = Graph().parse(_, 'text/turtle')
    _ = Semantics(g2, True, False, rdfs=True)
    # i think these are the datatype axioms (3rd arg)
    # false a rdfs:Literal,
    #     rdfs:Resource,
    #     xsd:boolean,
    #     owl:Thing ;
    # owl:sameAs false .
    # seems 'bad' https://www.w3.org/TR/rdf11-concepts/#section-triples
    _.closure()
    from rdflib.compare import graph_diff
    _ = graph_diff(g1, g2)
    diff = _[2] - _[1]
    _ = BytesIO()
    diff.serialize(_, 'text/turtle')
    del diff
    from pyoxigraph import Store, parse
    _.seek(0)
    diff = _
    _ = Store()
    breakpoint()
    _.load(diff, 'text/turtle')
    del diff
    _ = Triples(_)
    return _


# class OWLRL(PyRule):

#     def __init__(self, spec: PyRuleCallable) -> None:
#         super().__init__(spec)
