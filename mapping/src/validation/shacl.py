# pyshacl 'mode' to give generated data
# https://github.com/RDFLib/pySHACL/issues/60



def addnss(g, namespaces=()):
    for p,n in namespaces: g.bind(p, n)
    return g


from mapping.utils.queries import namespaces

def pyshacl(
    data, namespaces=namespaces(), shacl=None, ontology=None,
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

from pathlib import Path
from typing import Literal
from .engine import Triples
# could cache
def tqshacl(
        mode:Literal['validate']|Literal['infer'],
        data:'Triples', shapes:'Triples'=None,
        dir=Path.cwd(),) ->Triples:
    if mode == 'validate':
        from topquadrant import validate as f
    else:
        assert(mode == 'infer')
        from topquadrant import infer as f

    datap = dir / 'tqshacl.data.tmp.ttl'
    datap.unlink(missing_ok=True)
    from pyoxigraph import serialize
    serialize(data, datap, 'text/turtle')
    if shapes:
        shapesp = dir / 'tqshacl.shapes.tmp.ttl'
        shapesp.unlink(missing_ok=True)
        serialize(shapes, shapesp, 'text/turtle')
        o = f(datap, shapesp,)
    else:
        o = f(datap, )
    shapesp.unlink(missing_ok=True)
    datap.unlink(missing_ok=True)
    from mapping.utils.data import get_data
    o = get_data(o.stdout, )
    return o


