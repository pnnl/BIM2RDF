from typing import Tuple, Iterable

Point = Tuple[float, float, float]
def is_point_inside_points(
        pt:             Point,
        pts: Iterable[  Point ]) \
    -> bool:
    """inside ...or touching"""
    if len(pts) < 2:
        raise ValueError('need at least two pts to make sense')
    mnx = min(p[0] for p in pts)
    mny = min(p[1] for p in pts)
    mnz = min(p[2] for p in pts)
    mxx = max(p[0] for p in pts)
    mxy = max(p[1] for p in pts)
    mxz = max(p[2] for p in pts)
    cond = [
        (mnx <= pt[0] <= mxx),
        (mny <= pt[1] <= mxy),
        (mnz <= pt[2] <= mxz),]
    if all(cond):
        return True
    else:
        return False


def minmax_xyz(pts, coord='z', mm='min'):
    # some representative pt
    assert(mm in {'min', 'max'})
    xyz2i = {xyz:i for i,xyz in enumerate('xyz') }
    _ = sorted(pts, key=lambda p: p[xyz2i[coord]] )
    if mm == 'min':
        return _[0]
    else:
        return _[-1]
    raise ValueError


def list_to_pts(l):
    l = list(l)
    assert(not len(l) % 3)
    # take every 3rd
    xs = (l)[0::3]
    ys = (l)[1::3]
    zs = (l)[2::3]
    _ = zip(xs, ys, zs)
    _ = list(_)
    return _


def matmul(a,b):
    ar,ac = a.shape # n_rows * n_cols
    br,bc = b.shape # n_rows * n_cols
    assert ac==br # rows == columns
    #c = torch.zeros(ar, bc)
    for i in range(ar):
        for j in range(bc):
            for k in range(ac): # or br
                c[i,j] += a[i,k] * b[k,j]
    return c


class query(str): pass


def speckle_categoryq(cat) -> str:
    _ =  f'?s spkl:category "{cat}".' if cat else ""
    return _

def from_graph(graph:str=''):
    return ('from'+graph) if graph else ''


from speckle import base_uri


def meshesq(speckle_category=None, graph=None) -> query:
    # just go into the graph for the list
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    select ?s ?vl  (count(?f)-1 as ?pos) ?xyz {from_graph(graph)}
    where {{
    
    {speckle_categoryq(speckle_category)}
    ?s (!<urn:nothappening>)* ?m.  # connect ?s to the mesh in any way

    ?m spkl:speckle_type "Objects.Geometry.Mesh".
    ?m spkl:vertices/spkl:data* ?vl.
    #?vl rdf:rest*/rdf:first ?xyz.  # order not guaranteed!
    ?vl rdf:rest* ?f. ?f rdf:rest* ?n. # conects (first, next) ptrs to data list
    ?n rdf:first ?xyz.

    }}
    group by ?s ?vl ?n ?xyz
    order by ?vl ?pos
    """
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    select ?s ?vl  (count(?f)-1 as ?pos) ?xyz {from_graph(graph)}
    where {{
    
    {speckle_categoryq(speckle_category)}
    # path 'parts' must contain: dispalyValue, vertices, and data
    # connect them in whatever way
    # why not in  sparql can do like filepath wildcards?? .../*/...
    ?s spkl:displayValue/(!<urn:nothappening>)*/spkl:vertices/(!<urn:nothappening>)*/spkl:data ?vl.  # connect to displayValue
    #?m spkl:speckle_type "Objects.Geometry.Mesh".
    #?dc spkl:speckle_type "Speckle.Core.Models.DataChunk".
    #?m  spkl:vertices ?vl.
    #?vl rdf:rest*/rdf:first ?xyz.  # order not guaranteed!
    ?vl rdf:rest* ?f. ?f rdf:rest* ?n. # conects (first, next) ptrs to data list
    ?n rdf:first ?xyz.

    #filter(?s =spkl:b355f4bc783e05e4b29bb2482237ca36)

    }}
    group by ?s ?vl ?n ?xyz
    order by ?vl ?pos
    """
    _ = query(_)
    return _


# https://github.com/specklesystems/speckle-sharp/issues/1774
# deprecated
def baseptq(speckle_category=None, graph=None) -> query:
    _ = f"""
      PREFIX spkl: <http://speckle.systems/>
      select ?p ?x ?y ?z {from_graph(graph)}
        where {{
        {speckle_categoryq(speckle_category)}
        ?s (!<urn:nothappening>)* ?p. 

        ?p spkl:basePoint/spkl:x ?x.
        ?p spkl:basePoint/spkl:y ?y.
        ?p spkl:basePoint/spkl:z ?z.
        }}
    """
    _ = query(_)
    return _


def translationq(speckle_category=None, graph=None) -> query:
    _ = f"""
    PREFIX spkl: <{base_uri()}>

    select ?s  (count(?f)-1 as ?pos) ?xyz {from_graph(graph)}
    where {{
    
    {speckle_categoryq(speckle_category)}
    ?s (!<urn:nothappening>)*/spkl:matrix ?m.
    
    ?m rdf:rest* ?f. ?f rdf:rest* ?n.
    ?n rdf:first ?xyz.

    }}
    group by ?s ?m ?n ?xyz
    order by ?s ?m ?pos
    """
    _ = query(_)
    return _


from .engine import OxiGraph, Triples
def mesh_assignment(db: OxiGraph, point_catogory, mesh_category) -> Triples:
    def mqr(category):
        from collections import defaultdict
        mr = defaultdict(lambda : defaultdict(list))
        _ = db._store.query(meshesq(category))
        for thing, lst, i, xyz in _: mr[thing][lst].append(xyz)
        from itertools import chain
        for thing, lsts in mr.items():
            _ = chain.from_iterable(lsts.values())
            _ = map(lambda _: float(_.value ), _)
            _ = list_to_pts(_)
            mr[thing] = _
        return mr
    mr = mqr(mesh_category)
    return mr
    # for lighting fixtures i think the same mesh can be pointed to by
    #for pt, x, y, z in _:
        #return pt
        #for thing, pts in mr.items():
         #   if is_point_inside_points((x,y,z), pts):
          #      yield pt, thing


def test():
    from pyoxigraph import Store
    _ = Store()
    _.bulk_load('./work/out.ttl', 'text/turtle')
    _ =  OxiGraph(_)
    _ = mesh_assignment(_ , "Lighting Fixtures", "Rooms")
    return _
