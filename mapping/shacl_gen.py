# pyshacl 'mode' to give generated data
# https://github.com/RDFLib/pySHACL/issues/60


def shacl(
    data, shacl=None, ontology=None):
    from rdflib import Graph
    #    self,
    #     data_graph: GraphLike,
    #     *args,
    #     shacl_graph: Optional[GraphLike] = None,
    #     ont_graph: Optional[GraphLike] = None,
    #     options: Optional[dict] = None,
    #     **kwargs,
    from pathlib import Path
    if isinstance(data, Path) and Path(data).exists():
        data = Graph().parse(Path(data))
    elif isinstance(data, str):
        if data.startswith('http'):
            data = Graph().parse(data)
        else: # take it as ttl
            data = Graph().parse(data=data, format='ttl')
    elif isinstance(data, Graph):
        data = data
    else:
        raise TypeError('data source')
    from pyshacl.validate import Validator as _Validator
    v = _Validator(
            data,
            shacl_graph=Graph().parse(  shacl,)     if shacl    else None,
            ont_graph=Graph().parse(    ontology)   if ontology else None,
            options={'advanced': True}
            )
    from types import SimpleNamespace as NS
    validation = v.run()
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


if __name__ == '__main__':
    import fire
    fire.Fire(gen)

