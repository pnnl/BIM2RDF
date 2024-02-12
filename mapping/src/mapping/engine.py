"""
engine specialization
"""
from engine.triples import (
        ConstructQuery,
        ConstructRule as _ConstructRule, 
        Rules,
        Rule ,  # for owlrl TODO
        PyRule as _PyRule, PyRuleCallable,
        Triples, Iterable,
        Engine, OxiGraph)
from pyoxigraph import NamedNode, Triple, Literal as rdfLiteral

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

    def meta(self, ) -> Iterable[Triple]:
        yield from super().meta()
        p = meta_prefix
        fp = self.path.parts[-2:] # get the file plus its parent dir
        fp = '/'.join(fp)
        yield from [Triple(
                # TODO: add a name here to be like the pyrule
                #        watch that the fn is unique enough
                NamedNode(f'{p}/constructquery'),
                NamedNode(f'{p}/constructquery#name'),
                rdfLiteral(str(self.name))
                     )]

class PyRule(_PyRule):

    def meta(self, ) -> Iterable[Triple]:
        yield from super().meta()
        p = meta_prefix
        yield from [
            Triple(NamedNode(f'{p}/python#function'),
                NamedNode(f'{p}/python#name'),
                rdfLiteral(( self.name )),)
        ]

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
            #     1,    <== original 
            #     1.0 ; <== adds
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





def get_ontology(_: OxiGraph,) -> Triples:
    from .utils.data import get_data
    from project import root
    _ = get_data(root / 'models' / 'ontology.ttl'  ) # collection
    return _


def rdflib_rdfs(db: OxiGraph) -> Iterable[Triple]:
    s = db._store
    from .utils.queries import queries, select
    before = select(s, (
            queries.rules.mapped,
            queries.rules.ontology,
            queries.rules.rdfs_inferred,
            queries.rules.shacl_inferred) )
    from .utils.conversions import triples2ttl
    _ = triples2ttl(before)
    from rdflib import Graph
    _ = Graph().parse(data=_, format='text/turtle')
    assert(isinstance(_, Graph))
    _ = get_closure(_, semantics='rdfs')
    from .utils.conversions import rg2triples
    _ = rg2triples(_)
    after = frozenset(_)
    # only pick out triples from data
    before = frozenset(before)
    assert(len(after) >= len(before))
    _ = after - before; del before, after
    #return _
    # furhtermore only get data-inferred
    data = select(db._store, (
        queries.rules.mapped,
        queries.rules.rdfs_inferred,
        queries.rules.shacl_inferred
        ) )
    data = frozenset(data)
    from itertools import chain
    dataset = chain(
        frozenset(t[0] for t in data),
        #frozenset(t[1] for t in data),
        #frozenset(t[2] for t in data),
        )
    dataset = frozenset(dataset)
    del data
    _ = (t for t in _ if any(n in dataset for n in t) )
    return _


def topquadrant_rules(db: OxiGraph) -> Triples:
    s = db._store
    from .utils.queries import queries, select
    _ = select(s, (
            queries.rules.mapped,
            queries.rules.rdfs_inferred,
            queries.rules.shacl_inferred,
              ) ) #
    from pyoxigraph import parse
    from project import root
    shapes = parse(root / 'models'  / 'ontology.ttl', 'text/turtle' )
    from itertools import chain
    _ = chain(_, shapes)
    from validation.shacl import tqshacl
    _ = tqshacl('infer', _, )
    # could get some bnode issues b/c of
    # ttl reading back bnodse as different!!!
    # tq only returns new
    return _


def generated(before, after):
    #before = copy(_)
    # make sure 'before' is a copy of the orignial
    _ = (t for t in after if t not in before)
    from rdflib import Graph
    g = Graph()
    for t in _: g.add(t)
    return g
    # below is incredibly slow
    from .utils.rdflibgraph import graph_diff
    return graph_diff(before, after).in_generated



from functools import lru_cache
@lru_cache(1)
def shacl_defs(ontology_collection='defs'):
    from pyshacl.shapes_graph import ShapesGraph
    _ = get_ontology_collection('defs')
    #_ = _.skolemize()
    _ = ShapesGraph(_)
    _.shapes # finds rules. otherwise gather_rules errors
    from pyshacl.rules import gather_rules
    from pyshacl.functions import gather_functions
    class _():
        functions = gather_functions(_)
        rules =  gather_rules(_, iterate_rules=True)
    _ = _()
    return _

def addnss(g, namespaces=()):
    for p,n in namespaces: g.bind(p, n)
    return g

def pyshacl_rules(db: OxiGraph) -> Triples:
    # not working. needs to be wired back up. 
    from pyshacl.rules import apply_rules, gather_rules
    functions = shacl_defs().functions
    rules =  shacl_defs().rules
    _ = db._store
    from .utils.queries import queries, select
    _ = select(_, (
        queries.rules.mapped,
        #queries.rules.shacl_inferred)
        queries.rules.rdfs_inferred,
        ))
    from .conversions import og2rg
    _ = og2rg(_)
    from .utils.rdflibgraph import copy
    _ = copy(_) # backed by rdflib..which is 'safer'
    before = copy(_)
    from pyshacl.functions import gather_functions, apply_functions# , unapply_functions have to do these?
    apply_functions(functions, _)
    from .utils.queries import namespaces
    _ = addnss(_, namespaces=namespaces())
    apply_rules(rules, _, iterate=True)
    from .conversions import rg2triples
    _ = generated(before, _)
    _ = rg2triples(_)
    return _


if __name__ == '__main__':
    from pathlib import Path
    def semantics_infer(
            ipth: Path,
            semantics: str='rdfs',
            opath: Path=Path('inferred.ttl')):
        ipth = Path(ipth)
        g = Graph().parse(ipth, 'text/turtle')
        g = get_closure(g, semantics=semantics)
        g.serialize(opath, 'text/turtle')
        return opath
    
    def ontology(
            def_: str='ontology',
            infer: str|None ='rdfs',
            opath: Path=Path('ontology.ttl') ):
        from ontologies.collect import process
        _ = process(def_=def_, import_deps=True, remove_owl_imports=True)
        if infer:
            _ = get_closure(_, semantics=infer)
        _.serialize(opath, 'text/turtle')
        return opath
    
    from fire import Fire
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    logger.setLevel(logging.INFO)
    Fire(
        {
            'semantics_infer': semantics_infer,
            'ontology': ontology,
         })

