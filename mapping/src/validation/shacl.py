# pyshacl 'mode' to give generated data
# https://github.com/RDFLib/pySHACL/issues/60



def addnss(g, namespaces=()):
    for p,n in namespaces: g.bind(p, n)
    return g


def shacl(
    data, namespaces=(), shacl=None, ontology=None,
    advanced=False, iterate_rules=False,
    # logger=None doesn't work.
    ):
    # adding a thin layer of conveniences
    #    self,
    #     data_graph: GraphLike,
    #     *args,
    #     shacl_graph: Optional[GraphLike] = None,
    #     ont_graph: Optional[GraphLike] = None,
    #     options: Optional[dict] = None,
    #     **kwargs,
    def mg(g):
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
    from mapping.utils.rdflibgraph import graph_diff
    gd = graph_diff(data, v.target_graph).in_generated
    # clean the generated data, v.target_graph, after this
    return NS(
        validation=validation,
        generated=gd,)

