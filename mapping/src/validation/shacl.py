# pyshacl 'mode' to give generated data
# https://github.com/RDFLib/pySHACL/issues/60



from mapping.graphfix import Graph as FGraph
from rdflib import Graph as RGraph
def graph(g, mem=True) -> FGraph:
    from pathlib import Path
    if isinstance(g, Path) and Path(g).exists():
        g = FGraph().parse(Path(g))
    elif isinstance(g, str):
        if g.startswith('http'):
            g = FGraph().parse(g)
        else: # take it as ttl
            g = FGraph().parse(data=g, format='ttl')
    elif isinstance(g, (FGraph, RGraph) ):
        g = g
    else:
        raise TypeError('data source')
    if mem:
        # do your horrible mess in memory
        _ = FGraph() # but make it fixable
        for d in g: _.add(d) # (copying to memory)
        g = _
    return g


def addnss(g, namespaces=()):
    for p,n in namespaces: g.bind(p, n)
    return g


def graph_diff(data, generated):
    from collections import namedtuple
    GraphDiff = namedtuple('GraphDiff', ['in_both', 'in_data', 'in_generated'])
    from rdflib.compare import graph_diff as _graph_diff
    return GraphDiff(*_graph_diff(data, generated))


def shacl(
    data, namespaces=(), shacl=None, ontology=None,
    advanced=False, iterate_rules=False,
    # logger=None doesn't work.
    ):
    #    self,
    #     data_graph: GraphLike,
    #     *args,
    #     shacl_graph: Optional[GraphLike] = None,
    #     ont_graph: Optional[GraphLike] = None,
    #     options: Optional[dict] = None,
    #     **kwargs,
    def mg(g):
        g = graph(g)
        g = addnss(g, namespaces=namespaces)
        return g
    data = mg(data)
    from pyshacl.validate import Validator
    v = Validator(
            data,
            shacl_graph=mg(shacl)       if shacl    else None,
            ont_graph=  mg(ontology)    if ontology else None,
            options={'advanced': advanced, 'iterate_rules': iterate_rules,}# 'logger':logger}
            )
    from types import SimpleNamespace as NS
    validation = v.run() # (not nonconform), report:graph, text
    validation = NS(
        conforms=   validation[0],
        report=     validation[1],
        text=       validation[2])
    gd = graph_diff(data, v.target_graph).in_generated
    # clean the generated data, v.target_graph, after this
    return NS(
        validation=validation,
        generated=gd,
    )

