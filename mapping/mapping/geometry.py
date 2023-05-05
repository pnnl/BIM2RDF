
import numpy as np
def is_point_inside_points(
        pt:  np.ndarray,
        pts: np.ndarray) \
    -> bool:
    """inside ...or touching"""
    if len(pts) < 2:
        raise ValueError('need at least two pts to make sense')
    mins = pts.min(0)
    maxs = pts.max(0)
    cond = mins <= pt <= maxs
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


def in_hull(p, hull):
    #https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl/16898636#16898636
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """
    from scipy.spatial import Delaunay
    if not isinstance(hull,Delaunay):
        hull = Delaunay(hull)
    return hull.find_simplex(p)>=0 # test if inside


def score(comparison):
    s = sum(comparison)
    return s # could be 0


def compare(db: OxiGraph, cat1, cat2,):
    # generic approach: convex hull with all points of c1
    # but shortcut here is to just use the transform pt
    from itertools import product
    for (o1, geo1), (o2, geo2) in product(
                                category_array(db, cat1, 'transform').items(),
                                category_array(db, cat2, 'vertices').items() ):
        rep_pt1 = (geo1[xyz][-1] for xyz in range(3)) # just taking the translation part
        rep_pt1 = tuple(rep_pt1)
        yield o1, o2, in_hull(np.array([rep_pt1]), geo2)


def get_obj_assignment(db: OxiGraph, cat1, cat2):
    _ = compare(db, cat1, cat2)
    from collections import defaultdict
    inside = defaultdict(list)
    for o1, o2, c in tuple(_): inside[o1].append((o2, c))
    for o1, cs in inside.items():
        best = sorted(cs, key=lambda oc: score(oc[1]) )[-1]
        #                       consider 0 or None as total failue
        inside[o1] = best[0] if score(best[1]) else None
    return inside



def test():
    from pyoxigraph import Store
    _ = Store()
    _.bulk_load('./work/out.ttl', 'text/turtle')
    _ =  OxiGraph(_)
    _ = get_obj_assignment(_ , "Lighting Fixtures", "Rooms")
    return _
