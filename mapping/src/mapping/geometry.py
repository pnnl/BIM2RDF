

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


def branch_selector(cat,  branch=None):
    # need both to get the expected result!
    s = f'<<?s spkl:category "{cat}" >>'
    p = "meta:"
    o = f'<<?branch spkl:name "{branch}" >>'
    _ = f"{s} {p} {o}." if branch else ''
    s = f'<<?n rdf:first ?xyz >>'
    _ = _ + '\n' + (f"{s} {p} {o}." if branch else '')
    return _


from speckle import base_uri, meta_uri

def geoq(list_selector, branch_selector='', graph=None) -> query:  # add to group, the export
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX meta: <{meta_uri()}>
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

    {branch_selector}

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
    _ = (
        list_selector(category, lst2arr),
        branch_selector(category, 'electrical'))
    _ = geoq(*_)
    _ = db._store.query(_)
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


def in_hull(p, hull): # todo: concave hull
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
    import numpy as np
    # generic approach: convex hull with all points of c1
    # but shortcut here is to just use the transform pt
    from itertools import product
    for (o1, geo1), (o2, geo2) in product(
                                category_array(db, cat1, 'transform').items(),
                                category_array(db, cat2, 'vertices').items() ):
        rep_pt1 = (geo1[xyz][-1] for xyz in range(3)) # just taking the translation part
        rep_pt1 = tuple(rep_pt1)
        yield o1, o2, in_hull(np.array([rep_pt1]), geo2)


def get_obj_assignment_dict(db: OxiGraph, cat1, cat2) -> dict:
    _ = compare(db, cat1, cat2)
    from collections import defaultdict
    inside = defaultdict(list)
    for o1, o2, c in tuple(_): inside[o1].append((o2, c))
    for o1, cs in inside.items():
        best = sorted(cs, key=lambda oc: score(oc[1]) )[-1]
        #                       consider 0 or None as total failue
        inside[o1] = best[0] if score(best[1]) else None

    return inside


from functools import cache
@cache
def get_uri():
    ontology='223p' # TODO: std refs to s223
    from ontologies import get, namespaces
    _ = ontology
    _ = get(_)
    _ = [ns for ns in namespaces() if ns.path == _]
    _ = _[0]
    _ = _.namespaces()
    _ = [ns for ns in _ if ns.prefix == 's223']
    _ = _[0]
    _ = _.uri
    return _


from .engine import Triples
def assigment_triples(d: dict) -> Triples:
    import pyoxigraph as og
    u = get_uri()
    _ = [og.Triple(o2, og.NamedNode(u+'contains'), o1) for o1,o2 in d.items()]
    _ = Triples(_)
    return _


from typing import Callable
def get_obj_assignment_rule(cat1, cat2) -> Callable[[OxiGraph], Triples]:
    # o1 contains o2
    def r(db: OxiGraph,) -> Triples:
        _ = get_obj_assignment_dict(db, cat1, cat2)
        _ = assigment_triples(_)
        return _
    return r

