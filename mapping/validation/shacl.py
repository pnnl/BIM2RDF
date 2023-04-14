# pyshacl 'mode' to give generated data
# https://github.com/RDFLib/pySHACL/issues/60



from rdflib import Graph
def graph(g) -> Graph:
    from pathlib import Path
    if isinstance(g, Path) and Path(g).exists():
        g = Graph().parse(Path(g))
    elif isinstance(g, str):
        if g.startswith('http'):
            g = Graph().parse(g)
        else: # take it as ttl
            g = Graph().parse(data=g, format='ttl')
    elif isinstance(g, Graph):
        g = g
    else:
        raise TypeError('data source')
    return g



def shacl(
    data, shacl=None, ontology=None,
    advanced=False):
    #    self,
    #     data_graph: GraphLike,
    #     *args,
    #     shacl_graph: Optional[GraphLike] = None,
    #     ont_graph: Optional[GraphLike] = None,
    #     options: Optional[dict] = None,
    #     **kwargs,
    from pyshacl.validate import Validator as _Validator
    v = _Validator(
            graph(data),
            shacl_graph=graph(shacl,)   if shacl    else None,
            ont_graph=graph(ontology)   if ontology else None,
            options={'advanced': advanced}
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
    return NS(
        validation=validation,
        #data=v.target_graph,
        generated=graph_diff(data, v.target_graph).in_generated
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

