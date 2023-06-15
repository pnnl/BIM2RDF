"""
engine specialization
"""
from engine.triples import (
        ConstructQuery,
        Rules,
        Rule ,  # for owlrl TODO
        PyRule, PyRuleCallable,
        Triples,
        Engine, OxiGraph)


#https://github.com/RDFLib/OWL-RL/issues/53
# really want to sparql  this. TODO
# def rules(self, t, cycle_num):
#     """
#     Go through the RDFS entailment rules rdf1, rdfs4-rdfs12, by extending the graph.
#     :param t: A triple (in the form of a tuple).
#     :type t: tuple
#     :param cycle_num: Which cycle are we in, starting with 1. Can be used for some (though minor) optimization.
#     :type cycle_num: int
#     """
#     from rdflib import RDF, RDFS, Literal
#     s, p, o = t
#     # rdf1
#     self.store_triple((p, RDF.type, RDF.Property))
#     # rdfs4a
#     if cycle_num == 1:
#         self.store_triple((s, RDF.type, RDFS.Resource))
#     # rdfs4b
#     if cycle_num == 1:
#         if isinstance(o, Literal): return # dont make illegal rdf!!!!!!
#         self.store_triple((o, RDF.type, RDFS.Resource))
#     if p == RDFS.domain:
#         # rdfs2
#         for uuu, Y, yyy in self.graph.triples((None, s, None)):
#             self.store_triple((uuu, RDF.type, o))
#     if p == RDFS.range:
#         # rdfs3
#         for uuu, Y, vvv in self.graph.triples((None, s, None)):
#             self.store_triple((vvv, RDF.type, o))
#     if p == RDFS.subPropertyOf:
#         # rdfs5
#         for Z, Y, xxx in self.graph.triples((o, RDFS.subPropertyOf, None)):
#             self.store_triple((s, RDFS.subPropertyOf, xxx))
#         # rdfs7
#         for zzz, Z, www in self.graph.triples((None, s, None)):
#             self.store_triple((zzz, o, www))
#     if p == RDF.type and o == RDF.Property:
#         # rdfs6
#         self.store_triple((s, RDFS.subPropertyOf, s))
#     if p == RDF.type and o == RDFS.Class:
#         # rdfs8
#         self.store_triple((s, RDFS.subClassOf, RDFS.Resource))
#         # rdfs10
#         self.store_triple((s, RDFS.subClassOf, s))
#     if p == RDFS.subClassOf:
#         # rdfs9
#         for vvv, Y, Z in self.graph.triples((None, RDF.type, s)):
#             self.store_triple((vvv, RDF.type, o))
#         # rdfs11
#         for Z, Y, xxx in self.graph.triples((o, RDFS.subClassOf, None)):
#             self.store_triple((s, RDFS.subClassOf, xxx))
#     if p == RDF.type and o == RDFS.ContainerMembershipProperty:
#         # rdfs12
#         self.store_triple((s, RDFS.subPropertyOf, RDFS.member))
#     if p == RDF.type and o == RDFS.Datatype:
#        self.store_triple((s, RDFS.subClassOf, RDFS.Literal))
    
# RDFS_Semantics.rules = rules



from owlrl.CombinedClosure import RDFS_OWLRL_Semantics  as Semantics#, RDFS_Semantics, OWLRL_Semantics
#from owlrl.CombinedClosure import RDFS_Semantics as Semantics



from rdflib import Literal, Graph as _Graph
class Graph(_Graph):

    def __init__(self, *p, **k):
        self._offensive = set()
        super().__init__(*p, **k)

    def add(self, t):
        if isinstance(t[0], Literal):
            self._offensive.add(t)
        # so that it keeps working as usual
        return super().add(t)
    
def closure(self):
    """
    Generate the closure the graph. This is the real 'core'.

    The processing rules store new triples via the separate method :func:`.Core.store_triple` which stores
    them in the :code:`added_triples` array. If that array is empty at the end of a cycle,
    it means that the whole process can be stopped.

    If required, the relevant axiomatic triples are added to the graph before processing in cycles. Similarly
    the exchange of literals against bnodes is also done in this step (and restored after all cycles are over).
    """
    self.pre_process()

    # Handling the axiomatic triples. In general, this means adding all tuples in the list that
    # forwarded, and those include RDF or RDFS. In both cases the relevant parts of the container axioms should also
    # be added.
    if self.axioms:
        self.add_axioms()

    # Add the datatype axioms, if needed (note that this makes use of the literal proxies, the order of the call
    # is important!
    if self.daxioms:
        self.add_d_axioms()

    self.flush_stored_triples()

    # Get first the 'one-time rules', ie, those that do not need an extra round in cycles down the line
    self.one_time_rules()
    self.flush_stored_triples()

    # Go cyclically through all rules until no change happens
    new_cycle = True
    cycle_num = 0
    while new_cycle:
        # yes, there was a change, let us go again
        cycle_num += 1


        # go through all rules, and collect the replies (to see whether any change has been done)
        # the new triples to be added are collected separately not to interfere with
        # the current graph yet
        self.empty_stored_triples()

        # Execute all the rules; these might fill up the added triples array
        for t in self.graph:
            self.rules(t, cycle_num)

        # Add the tuples to the graph (if necessary, that is). If any new triple has been generated, a new cycle
        # will be necessary...
        new_cycle = len(self.added_triples) > 0

        # DEBUG: print the cycle number out
        if True:#self._debug:
            print(f"-semantics Cycle {cycle_num} added {len(self.added_triples)} triples.")

        for t in self.added_triples:
            self.graph.add(t)

    self.post_process()
    self.flush_stored_triples()

    # Add possible error messages
    if self.error_messages:
        # I am not sure this is the right vocabulary to use for this purpose, but I haven't found anything!
        # I could, of course, come up with my own, but I am not sure that would be kosher...
        self.graph.bind("err", "http://www.daml.org/2002/03/agents/agent-ont#")
        from rdflib import BNode, RDF
        from owlrl.Namespaces import ERRNS
        for m in self.error_messages:
            break # ............
            message = BNode() # ....this creates an inf loop bc it's different each time
            self.graph.add((message, RDF.type, ERRNS.ErrorMessage))
            self.graph.add((message, ERRNS.error, Literal(m)))

Semantics.closure = closure


from .conversions import og2rg, rg2og

#https://github.com/oxigraph/oxrdflib/issues/22

def rdflib_semantics(db: OxiGraph) -> Triples:
    #https://github.com/oxigraph/oxrdflib/blob/f0f0a110c58e8e82acd2eb0af5514392d2941596/oxrdflib/__init__.py#L20
    # store constructor deps on 'config'. should be able to just taks store
    #s._store = g._store
    # will need to copy b/c the rule iface is triples
    # rdflibg = Graph(s)
    to = 'text/turtle'
    g1 = og2rg(db._store)
    # copy
    g2 = Graph()
    for _ in g1: g2.add(_)
    _ = Semantics(g2, True, True, rdfs=True)
    # _._debug = True generates waaay to much.
    # i think these are the datatype axioms (3rd arg)
    # false a rdfs:Literal,
    #     rdfs:Resource,
    #     xsd:boolean,
    #     owl:Thing ;
    # owl:sameAs false .
    # seems 'bad' https://www.w3.org/TR/rdf11-concepts/#section-triples
    #_.closure()
    #_ = OWLRL_Extension_Trimming(g2, True, True, rdfs=True)
    _.closure()
    # take out _offensive triples
    for bad in g2._offensive: g2.remove(bad)
    from rdflib.compare import graph_diff
    _ = graph_diff(g1, g2)
    diff = _[2] - _[1]
    _ = BytesIO()
    diff.serialize(_, to)
    del diff
    from pyoxigraph import Store
    _.seek(0)
    diff = _
    _ = Store()
    _.load(diff, to) # where illegal rdf with literal subjects is an issue
    del diff
    _ = Triples(q.triple for q in _)
    return _


# could have created a class
# class OWLRL(PyRule):
#     def __init__(self, spec: PyRuleCallable) -> None:
#         super().__init__(spec)

from functools import lru_cache
@lru_cache(1)
def ontology():
    from ontologies import get
    _ = get('223p')
    from rdflib import Graph
    g = Graph()
    g.parse(_)
    return g



from pathlib import Path
from typing import Callable
ttl = str
from io import BytesIO
def get_data_getter(src: BytesIO | ttl | Path | Callable[[], ttl ]  ) ->  Callable[[OxiGraph], Triples]: # TODO: use pyrule
    from pyoxigraph import Store
    if isinstance(src, BytesIO):
        s = Store()
        s.bulk_load(src, 'text/turtle')
        _ = lambda _: Triples(q.triple for q in s)
        return _
    elif isinstance(src, ttl):
        _ = src.encode()
        _ = BytesIO(_)
        _ = get_data_getter(_)
        return _
    elif isinstance(src, Path):
        assert(src.suffix == '.ttl')
        _ = open(src, 'rb')
        _ = _.read()
        _ = BytesIO(_)
        _ = get_data_getter(_)
        return _
    elif callable(src):
        _ = src()
        _ = get_data_getter(_)
        return _
    else:
        raise ValueError('dont know how to get data')


def pyshacl_rules(db: OxiGraph) -> Triples:
    from validation.shacl import shacl
    #def shacl(
    #data, shacl=None, ontology=None,
    #advanced=False):
    _ = og2rg(db._store)
    _ = shacl(_, shacl=ontology(), advanced=True, iterate_rules=True )
    _ = _.generated
    _ = rg2og(_)
    _ = Triples(q.triple for q in _)
    return _



