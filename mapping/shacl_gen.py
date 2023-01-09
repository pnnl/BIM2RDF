# pyshacl 'mode' to give generated data
# https://github.com/RDFLib/pySHACL/issues/60

from pyshacl.validate import Validator



if __name__ == '__main__':
    import sys
    #    self,
    #     data_graph: GraphLike,
    #     *args,
    #     shacl_graph: Optional[GraphLike] = None,
    #     ont_graph: Optional[GraphLike] = None,
    #     options: Optional[dict] = None,
    #     **kwargs,
    from rdflib import Graph
    v = Validator(
            Graph().parse(sys.argv[1]), 
            shacl_graph=Graph().parse(sys.argv[2]),
            options={'advanced': True}
            )
    _ = v.run()
    v.target_graph.serialize('generated.ttl')


