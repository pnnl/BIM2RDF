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
        for d in g: _.add(d)
        g = _
    return g


def shacl(
    data, namespaces=(), shacl=None, ontology=None,
    advanced=False, iterate_rules=False):
    #    self,
    #     data_graph: GraphLike,
    #     *args,
    #     shacl_graph: Optional[GraphLike] = None,
    #     ont_graph: Optional[GraphLike] = None,
    #     options: Optional[dict] = None,
    #     **kwargs,
    def addnss(g):
        for p,n in namespaces: g.bind(p, n)
        return g

    from pyshacl.validate import Validator as _Validator
    data = addnss(graph(data))
    v = _Validator(
            data,
            shacl_graph=addnss(graph(shacl,))   if shacl    else None,
            ont_graph=addnss(graph(ontology))   if ontology else None,
            options={'advanced': advanced, 'iterate_rules': iterate_rules}
            )
    from types import SimpleNamespace as NS
    validation = v.run() # (not nonconform), report:graph, text
    validation = NS(
        conforms=   validation[0],
        report=     validation[1],
        text=       validation[2])
    from rdflib.compare import graph_diff as _graph_diff
    from collections import namedtuple
    GraphDiff = namedtuple('GraphDiff', ['in_both', 'in_data', 'in_generated'])
    def graph_diff(data, generated):
        return GraphDiff(*_graph_diff(data, generated))
    # clean the generated data, v.target_graph, after this
    return NS(
        validation=validation,
        #data=v.target_graph,
        generated=(graph_diff(data, v.target_graph).in_generated)
    )
    #if out
    #_ = v.run()
    #return v
    #if out_type == 'data':
        #v.target_graph.serialize(out)
    #else: #put out the validation graph
        # is it this?


# if __name__ == '__main__':
#     import fire
#     fire.Fire(shacl)

