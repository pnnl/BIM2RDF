"""
engine specialization
"""
from engine.triples import (
        ConstructQuery,
        ConstructRule as _ConstructRule, 
        Rules,
        Rule ,  # for owlrl TODO
        PyRule as _PyRule, PyRuleCallable,
        Triples,
        Engine, OxiGraph)


meta_prefix = 'http://mmeta'

def namespaces():
    from ontologies import namespace
    from rdflib import URIRef
    return (
        namespace('mmeta', URIRef(meta_prefix)),
    )

class ConstructRule(_ConstructRule):

    def __init__(self, path) -> None:
        from pathlib import Path
        path = Path(path).absolute()
        self.path = path
        # for the mapping case, we're starting from the file
        spec = open(path).read()
        super().__init__(spec)
    
    @property
    def name(self):
        from project import root
        _ = self.path.relative_to(root).as_posix()
        return _
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def meta(self, data: Triples) -> Triples:
        yield from super().meta(data)
        from pyoxigraph import NamedNode, Triple, Literal
        p = meta_prefix
        fp = self.path.parts[-2:] # get the file plus its parent dir
        fp = '/'.join(fp)
        yield from Triples([Triple(
                # TODO: add a name here to be like the pyrule
                #        watch that the fn is unique enough
                NamedNode(f'{p}/constructquery'),
                NamedNode(f'{p}/constructquery#name'),
                Literal(str(self.name))
                     )])

class PyRule(_PyRule):

    def meta(self, data: Triples) -> Triples:
        yield from super().meta(data)
        from pyoxigraph import NamedNode, Triple, Literal
        p = meta_prefix
        yield from Triples([
            Triple(NamedNode(f'{p}/python#function'),
                NamedNode(f'{p}/python#name'),
                Literal(( self.name )),)
        ])



import logging 
logger = logging.getLogger('mapping_engine')



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



def closure(self):
    # adding for logging and controlling error messages
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
            logger.info(f"semantics Cycle {cycle_num} added {len(self.added_triples)} triples.")

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

from typing import Literal
def get_rdflib_semantics(semantics:Literal['owlrl']|Literal['rdfs']  ):
    #from owlrl import (
    #RDFS_OWLRL_Semantics,  below problem. plus better to have the two separate
    # OWLRL_Extension_Trimming, does not add illegal triples?
    #RDFS_Semantics,
    #OWLRL_Semantics, 
    #)
    #return_closure_class(owl_closure, rdfs_closure, owl_extras, trimming=False)
    if semantics == 'owlrl':
        from owlrl import OWLRL_Semantics as S
    elif semantics == 'rdfs':
        from owlrl import RDFS_Semantics as S
        # it messes up these!
            # sh:maxCount true, 
            #     1,  <== original 
            #     1.0 ;
        # stop the nonsense
        def _(*a, **p): ...
        S.one_time_rules = _ 
    else:
        raise ValueError('semantics not selected')
    S.closure = closure
    return S

def get_closure(g, semantics='rdfs',
        improved_datatypes=True,
        axiomatic_triples=True,
        datatype_axioms=False,
                ):
    semantics = get_rdflib_semantics(semantics)
    from owlrl import DeductiveClosure
    DeductiveClosure(
        semantics,
        # fixed
        rdfs_closure=False,  #only used with non-rdfs semantics.
        # could vary
        improved_datatypes=improved_datatypes,
        axiomatic_triples=axiomatic_triples,
        datatype_axioms=datatype_axioms,
        ).expand(g)
    g = fix(g) #put it here or in the rule
    return g


from rdflib import Graph
def fix(g: Graph) -> Graph:
    from rdflib import Literal
    def bad(t):
        s, p, o = t
        if isinstance(s, Literal):
            return True
        return False        
    bads = {t for t in g if bad(t) }
    for t in bads: g.remove(t)
    return g

# could have created a class
# class OWLRL(PyRule):
#     def __init__(self, spec: PyRuleCallable) -> None:
#         super().__init__(spec)


def rdflib_rdfs(db: OxiGraph) -> Triples:
    _ = db._store
    from .utils.queries import queries
    _ = select(_, (
            queries.rules.mapped,
            queries.rules.ontology, # need all right?
            #queries.rules.rdfs_inferred,
            queries.rules.shacl_inferred) )
    from .conversions import og2rg
    _ = og2rg(_) # backed by oxygraph
    from .utils.rdflibgraph import copy
    _ = copy(_) # backed by rdflib..which is 'safer'
    #before = copy(_)
    _ = get_closure(_, semantics='rdfs')
    # from .utils.rdflibgraph import graph_diff
    # _ = graph_diff(before, _).in_generated
    #_ = fix(_) put it here or in rdfs?
    from .conversions import rg2triples
    _ = rg2triples(_)
    return _




from pyoxigraph import Store
def select(store: Store, construct_queries) -> Store:
    queries = construct_queries
    _ = []
    for q in queries:
        _.extend(store.query( q  ))
    s = Store()
    from pyoxigraph import Quad
    if len(_): s.bulk_extend(Quad(*t) for t in _)
    return s


from functools import lru_cache
@lru_cache(1)
def rgontology(): # rdflib graph ontology
    from ontologies import get
    _ = get('defs')
    from rdflib import Graph
    g = Graph()
    g.parse(_)
    return g


from functools import lru_cache
@lru_cache(1)
def shape_graph():
    from pyshacl.shapes_graph import ShapesGraph
    _ = rgontology()
    #_ = _.skolemize()
    _ = ShapesGraph(_)
    _.shapes # finds rules. otherwise gather_rules errors
    return _


def pyshacl_rules(db: OxiGraph) -> Triples:
    from validation.shacl import graph, graph_diff
    from pyshacl.rules import apply_rules, gather_rules
    from pyshacl.functions import gather_functions, apply_functions
    shacl = shape_graph() #queries.rules.ontology,
    functions = gather_functions(shacl)
    rules =  gather_rules(shacl, iterate_rules=True)
    _ = db._store
    from .utils.queries import queries
    _ = select(_, (
        queries.rules.mapped,
        queries.rules.rdfs_inferred,
        ))
        #queries.rules.shacl_inferred) 
    from .conversions import og2rg, rg2og
    _ = og2rg(_)
    before = graph(_)
    after = graph(_)
    apply_functions(functions, after)
    apply_rules(rules, after, iterate=True)
    _ = graph_diff(before, after).in_generated
    _ = rg2og(_)
    _ = Triples(q.triple for q in _)
    return _


if __name__ == '__main__':
    from pathlib import Path
    def infer(ttl:Path, semantics='rdfs', o:Path=Path('inferred.ttl')):
        from rdflib import Graph
        _ = Graph()
        _.parse(ttl)
        _ = get_closure(_, semantics=semantics)
        _.serialize(o)
        return _

    from fire import Fire
    Fire({'infer': infer})
