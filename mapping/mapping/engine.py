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


# def add_d_axioms(self):
#     from owlrl.AxiomaticTriples import RDFS_D_Axiomatic_Triples
#     from rdflib import RDF
#     """
#     This is not really complete, because it just uses the comparison possibilities that RDFLib provides.
#     """
#     # #1
#     literals = (lt for lt in self._literals() if lt.datatype is not None)
#     for lt in literals:
#         shouldbehere
#         # dont make illegal rdf!!!
#         self.graph.add((lt, RDF.type, lt.datatype))
#     for t in RDFS_D_Axiomatic_Triples:
#         #fine
#         self.graph.add(t)
# RDFS_Semantics.add_axioms = add_d_axioms
# def _literals(_): return set()
# Semantics._literals = _literals # this wasn't enough
# RDFS_Semantics._literals = _literals
# OWLRL_Semantics._literals = _literals

# #Semantics.add_d_axioms = add_d_axioms


# def flush_stored_triples(self):
#     """
#     Send the stored triples to the graph, and empty the container.
#     """
#     from rdflib import Literal
#     for t in self.added_triples:
#         # dont make illegal rdf!!!
#         #if isinstance(t[0], Literal):
#         if isinstance(t[0].toPython(), (int, str, bool, float) ):
#             print(t[0])
#             #breakpoint()
#             continue
#         self.graph.add(t)
#     self.empty_stored_triples()
# Semantics.flush_stored_triples = flush_stored_triples


def post_process(self):
    """
    Do some post-processing step performing the trimming of the graph. See the :class:`.OWLRL_Extension_Trimming`
    class for further details.
    """
    from rdflib import OWL, RDFS, RDF
    from owlrl.OWLRLExtras import OWLRL_Extension
    from owlrl.XsdDatatypes import OWL_RL_Datatypes
    from owlrl.OWLRL import OWLRL_Annotation_properties
    OWLRL_Extension.post_process(self)
    self.flush_stored_triples()

    to_be_removed = set()
    for t in self.graph:
        s, p, o = t
        if s == o:
            if (
                p == OWL.sameAs
                or p == OWL.equivalentClass
                or p == RDFS.subClassOf
                or p == RDFS.subPropertyOf
            ):
                to_be_removed.add(t)
        if (
            (p == RDFS.subClassOf and (o == OWL.Thing or o == RDFS.Resource))
            or (p == RDF.type and o == RDFS.Resource)
            or (s == OWL.Nothing and p == RDFS.subClassOf)
        ):
            to_be_removed.add(t)

    for dt in OWL_RL_Datatypes:
        # see if this datatype appears explicitly in the graph as the type of a symbol
        if len([s for s in self.graph.subjects(RDF.type, dt)]) == 0:
            to_be_removed.add((dt, RDF.type, RDFS.Datatype))
            to_be_removed.add((dt, RDF.type, OWL.DataRange))

            for t in self.graph.triples((dt, OWL.disjointWith, None)):
                to_be_removed.add(t)
            for t in self.graph.triples((None, OWL.disjointWith, dt)):
                to_be_removed.add(t)

    for an in OWLRL_Annotation_properties:
        self.graph.remove((an, RDF.type, OWL.AnnotationProperty))

    to_be_removed.add((OWL.Nothing, RDF.type, OWL.Class))
    to_be_removed.add((OWL.Nothing, RDF.type, RDFS.Class))
    to_be_removed.add((OWL.Thing, RDF.type, OWL.Class))
    to_be_removed.add((OWL.Thing, RDF.type, RDFS.Class))
    to_be_removed.add((OWL.Thing, OWL.equivalentClass, RDFS.Resource))
    to_be_removed.add((RDFS.Resource, OWL.equivalentClass, OWL.Thing))
    to_be_removed.add((OWL.Class, OWL.equivalentClass, RDFS.Class))
    to_be_removed.add((OWL.Class, RDFS.subClassOf, RDFS.Class))
    to_be_removed.add((RDFS.Class, OWL.equivalentClass, OWL.Class))
    to_be_removed.add((RDFS.Class, RDFS.subClassOf, OWL.Class))
    to_be_removed.add((RDFS.Datatype, RDFS.subClassOf, OWL.DataRange))
    to_be_removed.add((RDFS.Datatype, OWL.equivalentClass, OWL.DataRange))
    to_be_removed.add((OWL.DataRange, RDFS.subClassOf, RDFS.Datatype))#OWL.Datatype))
    to_be_removed.add((OWL.DataRange, OWL.equivalentClass, RDFS.Datatype))#OWL.Datatype))

    for t in to_be_removed:
        self.graph.remove(t)

from owlrl.CombinedClosure import RDFS_OWLRL_Semantics  as Semantics#, RDFS_Semantics, OWLRL_Semantics
#from owlrl.CombinedClosure import RDFS_Semantics as Semantics
from owlrl.OWLRLExtras import OWLRL_Extension_Trimming 

OWLRL_Extension_Trimming.post_process = post_process


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


from .conversions import og2rg

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

def get_shapes():
    from rdflib import Graph
    from ontologies import get as geto
    o = geto('223p')
    o = Graph().parse(o)
    from pyshacl import ShapesGraph
    _ = ShapesGraph(o)
    return _


from rdflib.plugins.sparql.processor import SPARQLResult
def get_shacl_triple_rules() -> SPARQLResult:
    # simple
    # something sh:rule [ a sh:TripleRule ;
    #         rdfs:comment "Cooling coils will always have the role Role-Cooling" ;
    #         sh:object s223:Role-Cooling ;
    #         sh:predicate s223:hasRole ;
    #         sh:subject sh:this ],
    # s223:MeasuredPropertyRule a sh:NodeShape ;
    # rdfs:comment "Associate the object of hasMeasurementLocation directly with the observed Property." ;
    # sh:rule [ a sh:TripleRule ;
    #         rdfs:comment "Associate the object of hasMeasurementLocation directly with the observed Property." ;
    #         sh:object [ sh:path ( [ sh:inversePath s223:hasMeasurementLocation ] s223:observes ) ] ;
    #         sh:predicate s223:hasProperty ;
    #         sh:subject sh:this ],
    from rdflib import Graph
    from ontologies import get as geto
    o = geto('223p')
    o = Graph().parse(o)
    ns = """
    ?s a sh:NodeShape.
    ?s sh:rule [a sh:TripleRule;
                sh:subject sh:this;
                sh:predicate ?p;
                sh:object ?os
                  ;].
    ?os ?op ?oo.
    """
    nsw =ns#.replace('?o', "?_o")
    #rdfs:comment ?comment;  # part of meta TODO: optional
    # https://stackoverflow.com/questions/37186530/how-do-i-construct-get-the-whole-sub-graph-from-a-given-resource-in-rdf-graph
    # wooooowww! (:|!:)* 
    #https://gist.github.com/tomsaleeba/ff8e145b3efd1127e48baa6512df24e2
    #?s2 (!<urn:nothing>)+ [] . # any length property path where the property != "something it will never equal" (i.e. find everything)
    r = o.query(f"""
    prefix sh: <http://www.w3.org/ns/shacl#>
    #prefix : <urn:ex:>
    construct {{{ns}}}
    where {{{nsw}
        #?os sh:path ?oo.
        ?os (!<urn:never>)* [].
        ?os ?op ?oo.
       }}
    """)
    return r


def get_shacl_sparql_rules() -> SPARQLResult:
#     s223:CorrelatedColorTemperatureSensor a s223:Class,
#         sh:NodeShape ;
#     rdfs:label "Correlated color temperature sensor" ;
#     rdfs:subClassOf s223:LightSensor ;
#     sh:rule [ a sh:SPARQLRule ;
#             rdfs:comment "A CorrelatedColorTemperatureSensor will always observe a Property that has a QuantityKind of ThermodynamicTemperature." ;
#             sh:construct """\r
# CONSTRUCT {?prop qudt:hasQuantityKind qudtqk:ThermodynamicTemperature .}\r
# WHERE {\r
#   $this s223:observes ?prop .\r
# }\r
# sh:prefixes <http://data.ashrae.org/standard223/1.0/extension/equipments-extensions-rules> ],
# """ ;
# prefixes
# <http://data.ashrae.org/standard223/1.0/extension/equipments-extensions-rules>
#   a owl:Ontology ;
#   owl:imports <http://data.ashrae.org/standard223/1.0/model/all> ;
#   sh:declare [
#       sh:namespace "http://data.ashrae.org/standard223#"^^xsd:anyURI ;
#       sh:prefix "s223" ;
#     ] ;
#   sh:declare [
#       sh:namespace "http://data.ashrae.org/standard223/1.0/vocab/role#"^^xsd:anyURI ;
#       sh:prefix "role" ;
#     ] ;
#   sh:declare [
#       sh:namespace "http://qudt.org/vocab/quantitykind/"^^xsd:anyURI ;
#       sh:prefix "qudtqk" ;
#     ] ;
#   sh:declare [
#       sh:namespace "http://qudt.org/vocab/unit/"^^xsd:anyURI ;
#       sh:prefix "unit" ;
#     ] ;
#   sh:declare [
#       sh:namespace "http://www.w3.org/2000/01/rdf-schema#"^^xsd:anyURI ;
#       sh:prefix "rdfs" ;
#     ] ;
# .
    from rdflib import Graph
    from ontologies import get as geto
    o = geto('223p')
    o = Graph().parse(o)
    r = o.query("""
    prefix sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    select distinct ?q ?pfx ?ns  where {
        ?s a sh:NodeShape.
        ?s sh:rule [a sh:SPARQLRule;
            sh:construct ?q;
            #rdfs:comment ?comment;  # part of meta TODO: optional
            #sh:prefixes ?pfxs;   # depends on author being proper
        ].
        ?pfxs a owl:Ontology.
        ?pfxs sh:declare [
            sh:namespace ?ns;
            sh:prefix    ?pfx;
        ].
    }
    """)
    return r


from typing import Iterable
def make_shacl_sparql_constructs(results= get_shacl_sparql_rules) -> Iterable[ConstructQuery]:
    queries = {}
    for q, pfx, ns in results():
        if q not in queries:
            queries[q] = {pfx: ns}
        else:
            queries[q][pfx] = ns
    
    # squishing everything
    #namespaces = {}
    #for ns in queries.values(): namespaces.update(ns)
    #return namespaces
    # use rdflib utils to parse the sparql construct
    #import rdflib.plugins.sparql.parser as  sp
    #import rdflib.plugins.sparql.algebra as sa
    for q in queries:
        namespaces = queries[q] #dpends on author being proper. consider getting directly from files with ontologies.namespaces
        #namespaces = namespaces
        _ = '\n'.join(f"PREFIX {pfx}:<{ns}>" for pfx,ns in namespaces.items() )  + str(q)
        #_ = sp.parseQuery(_)
        #_ = sa.translateQuery(_)
        # weid function that uses a file
        #_ = sa.translateAlgebra(_) # https://github.com/RDFLib/rdflib/pull/2267 eliminate file intermdiaary todo
        _ = ConstructQuery(_)
        yield _


def make_shaclrule_constructs() -> Iterable[ConstructQuery]:
    for s, p, o in (get_shacl_triple_rules()):
        #PyRule()
        q = make_construct_query(
            f"?this <{p}> <{o}>.", # construct
            f"?this a <{s}>.")    # where
        q = ConstructQuery(q)
        yield q
    yield from make_shacl_sparql_constructs()


def make_construct_query(construct: str, where: str=""):
    #lol @ triple brackets: two to escape. third for the var
    _ = f"""
    construct {{{construct}}}
    where {{{where}}}
    """
    return _


from pyshacl import Shape # ShapesGraph
from pyshacl.helper.sparql_query_helper import SPARQLQueryHelper


def test():
    _ = get_shapes()
    return _
    for s in _.shapes:
        _ = SPARQLQueryHelper(s, 'node', 'select_text')    
        return _


# https://github.com/RDFLib/pySHACL/blob/b31e9f6c667ce72ceab3e8a14cf46dcc51810045/pyshacl/helper/sparql_query_helper.py
def shacl_path_to_sparql_path(shape: Shape, prefixes={}, recursion=0):
    #path_val is arg
    """
    :param path_val:
    :type path_val: rdflib.term.Node
    :param recursion:
    :type recursion: int
    :returns: string
    :rtype: str
    """
    from pyshacl.consts import (
    OWL_PFX,
    RDF_PFX,
    RDFS_PFX,
    SH,
    OWL_Ontology,
    RDF_type,
    SH_alternativePath,
    SH_inversePath,
    SH_namespace,
    SH_oneOrMorePath,
    SH_prefix,
    SH_prefixes,
    SH_zeroOrMorePath,
    SH_zeroOrOnePath,)
    from pyshacl.errors import ConstraintLoadError, ReportableRuntimeError, ValidationFailure
    import rdflib
    #from pyshacl

    sg = self.shape.sg
    # Link: https://www.w3.org/TR/shacl/#property-paths
    if isinstance(path_val, rdflib.URIRef):
        string_uri = str(path_val)
        for p, ns in self.prefixes.items():
            if string_uri.startswith(ns):
                string_uri = ':'.join([p, string_uri.replace(ns, '')])
                return string_uri
        return "<{}>".format(string_uri)
    elif isinstance(path_val, rdflib.Literal):
        raise ReportableRuntimeError("Values of a property path cannot be a Literal.")
    # At this point, path_val _must_ be a BNode
    # TODO, the path_val BNode must be value of exactly one sh:path subject in the SG.
    if recursion >= 10:
        raise ReportableRuntimeError("Path traversal depth is too much!")
    sequence_list = list(sg.graph.items(path_val))
    if len(sequence_list) > 0:
        all_collected = []
        for s in sequence_list:
            seq1_string = self._shacl_path_to_sparql_path(s, recursion=recursion + 1)
            all_collected.append(seq1_string)
        if len(all_collected) < 2:
            raise ReportableRuntimeError("List of SHACL sequence paths must have alt least two path items.")
        return "/".join(all_collected)

    find_inverse = set(sg.objects(path_val, SH_inversePath))
    if len(find_inverse) > 0:
        inverse_path = next(iter(find_inverse))
        inverse_path_string = self._shacl_path_to_sparql_path(inverse_path, recursion=recursion + 1)
        return "^{}".format(inverse_path_string)

    find_alternatives = set(sg.objects(path_val, SH_alternativePath))
    if len(find_alternatives) > 0:
        alternatives_list = next(iter(find_alternatives))
        all_collected = []
        for a in sg.graph.items(alternatives_list):
            alt1_string = self._shacl_path_to_sparql_path(a, recursion=recursion + 1)
            all_collected.append(alt1_string)
        if len(all_collected) < 2:
            raise ReportableRuntimeError("List of SHACL alternate paths must have alt least two path items.")
        return "|".join(all_collected)

    find_zero_or_more = set(sg.objects(path_val, SH_zeroOrMorePath))
    if len(find_zero_or_more) > 0:
        zero_or_more_path = next(iter(find_zero_or_more))
        zom_path_string = self._shacl_path_to_sparql_path(zero_or_more_path, recursion=recursion + 1)
        return "{}*".format(zom_path_string)

    find_zero_or_one = set(sg.objects(path_val, SH_zeroOrOnePath))
    if len(find_zero_or_one) > 0:
        zero_or_one_path = next(iter(find_zero_or_one))
        zoo_path_string = self._shacl_path_to_sparql_path(zero_or_one_path, recursion=recursion + 1)
        return "{}?".format(zoo_path_string)

    find_one_or_more = set(sg.objects(path_val, SH_oneOrMorePath))
    if len(find_one_or_more) > 0:
        one_or_more_path = next(iter(find_one_or_more))
        oom_path_string = self._shacl_path_to_sparql_path(one_or_more_path, recursion=recursion + 1)
        return "{}+".format(oom_path_string)

    raise NotImplementedError("That path method to get value nodes of property shapes is not yet implemented.")