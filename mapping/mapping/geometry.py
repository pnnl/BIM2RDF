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

from typing import Literal
def list_selector(cat: str, cat_to_list: Literal['vertices'] | Literal['transform'] ) -> str:
    #                                    could still add faces here TODO
    # room vertices
    #?s spkl:category "Rooms".
    # ?s spkl:displayValue/(!<urn:nothappening>)*/spkl:vertices/(!<urn:nothappening>)*/spkl:data ?vl.
    
    # lighitng fixture vertices
    #?s spkl:category "Lighting Fixtures".
    #?s spkl:definition/spkl:displayValue/(!<urn:nothappening>)*/spkl:vertices/(!<urn:nothappening>)*/spkl:data ?vl.
    
    # lighting fixture transform
    #?s spkl:category "Lighting Fixtures".
    #?s spkl:transform/spkl:matrix ?vl.

    # pattern: 1. category spec 2. cat2list
    # defaults
    catl = f'\n ?s spkl:category "{cat}".'
    _to_list = 'spkl:displayValue/(!<urn:nothappening>)*/spkl:vertices/(!<urn:nothappening>)*/spkl:data ?vl.'
    if cat_to_list == 'vertices':
        to_list = "?s " +  _to_list
    else:
        assert(cat_to_list == 'transform')
        to_list = "?s spkl:transform/spkl:matrix ?vl."

    # specific
    if (cat == 'Lighting Fixtures') and (cat_to_list == 'vertices'):
        to_list = "?s spkl:definition/"+_to_list
    
    assert('?s' in catl)
    assert('?s' in to_list)
    return '\n'.join([catl, to_list])


def from_graph(graph:str=''):
    return ('from'+graph) if graph else ''


from speckle import base_uri

def geoq(list_selector, graph=None) -> query:
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    select ?s ?vl  (count(?f)-1 as ?pos) ?xyz {from_graph(graph)}
    where {{
    
    {list_selector}
    # path 'parts' must contain: dispalyValue, vertices, and data
    # connect them in whatever way
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


from .engine import OxiGraph
def category_array(db: OxiGraph, category, lst2arr):
    from numpy import  array
    from collections import defaultdict
    mr = defaultdict(lambda : defaultdict(list))
    selector = list_selector(category, lst2arr)
    _ = db._store.query(geoq(selector))
    for thing, lst, i, xyz in _: mr[thing][lst].append(xyz)
    from itertools import chain
    if   lst2arr == 'vertices':     shape = (-1, 3)
    elif lst2arr == 'transform':    shape = (4,4)
    else:                           shape = (-1,) # nothing
    #else: raise ValueError(f'unknown list2  {lst}')
    for thing, lsts in mr.items():
        _ = chain.from_iterable(lsts.values())
        _ = map(lambda _: float(_.value ), _)
        _ = tuple(_)
        _ = array(_)
        _ = _.reshape(*shape)
        mr[thing] = _
    return mr


def are_objs_inside(db: OxiGraph, cat1, cat2):
    # general case

    # maybe special cases
    #if (cat1 == 'Lighting Fixtures') and (cat2 == 'Rooms'):


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
