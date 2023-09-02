
class query(str): pass

def has_property(store, property, category=None, subject=None):
    # objects in the speckle sense (not semantic)
    #no need for branch and graph specifiers
    if (not category) and (not subject):
        raise ValueError('supply either cat or subject')
    if subject:
        subject = str(subject)
        assert(subject.startswith('<'))
        assert(subject.endswith(  '>'))
    else:
        subject = '?s'
    if subject:
        categoryline = ""
    else:
        categoryline = f"""{subject} spkl:category "{category}"."""
    _ = f"""
    {prefixes()}
    select ?v
    where {{
        {subject} spkl:{property} ?v.
        {categoryline}
    }}
    limit 1
    """
    _ = query(_)
    _ = store.query(_)
    _ = tuple(r[0] for r in _)
    assert(len(_) in {0, 1})
    if _: return _[0]


from typing import Literal
def lists_selector(subject: str,
                   cat_to_list: Literal['vertices'] | Literal['transform'] | Literal['definition/vertices'], ) -> str:
    #                                    could still add faces here TODO
    # when encountering a list
    # /path/to/list/rdf:rest*/rdf:first ?item.
    
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
    s = subject
    #                 displayValue --> List --> Vertices --> List --> data --> ?List
    _to_list = 'spkl:displayValue/rdf:rest*/rdf:first/spkl:vertices/rdf:rest*/rdf:first/spkl:data ?vl.'
    if 'vertices' == cat_to_list:
        to_list = f"{s} " +  _to_list
    elif cat_to_list == 'definition/vertices':
        # if has transform, then need to go through def
    #if (cat == 'Lighting Fixtures') and (cat_to_list == 'vertices'):
        to_list = f"{s} spkl:definition/"+_to_list
    else:
        assert(cat_to_list == 'transform')
        #                    transform ->  maxtrix ->  ?List
        to_list = f"{s} spkl:transform/spkl:matrix ?vl."
    assert(f"{s}" in to_list)
    return '\n'.join([to_list])


def from_graph(graph:str=''):
    return ('from'+graph) if graph else ''


def geo_branch_selector(branch=None):
    s = f'<<?n rdf:first ?xyz >>'
    p = "meta:"
    o = f'<<?branch spkl:name "{branch}" >>'  # branchName could be used here TODO
    _ = f"{s} {p} {o}." if branch else ''
    return _


from speckle import base_uri, meta_uri


def prefixes():
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX meta: <{meta_uri()}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    """
    return _


def objectsq(cat, branch=None, graph=None):
    # objects in the speckle sense (not semantic)
    _ = f"?s spkl:category \"{cat}\""
    if branch:
        bl = f"""<< {_} >> meta: <<?branch spkl:name "{branch}" >>."""
    else:
        bl = ''
    _ = f"""
    {prefixes()}

    select distinct ?s {from_graph(graph)}
    where {{
        {_}.
        {bl}
    }}
    """ # branchName could be used here TODO
    _ = query(_)
    return _


def get_objects(store, cat, branch=None, graph=None):
    # fast enough query
    _ = objectsq(cat, branch=branch, graph=graph)
    _ = store.query(_)
    return tuple(r[0] for r in _)


def geoq(subject, list_selector, branch_selector='', graph=None, ) -> query:  # add to group, the export
    # single object at a time to not load all geometry in one query
    # using values seems to help with performance. (using filter was too slow)
    # need branch selector if have subject?
    _ = f"""
    {prefixes()}

    select ?vl  (count(?f)-1 as ?pos) ?xyz {from_graph(graph)}
    where {{
    
    values ?s {{ {subject} }}
    
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
    group by ?vl ?n ?xyz
    order by ?vl ?pos
    """
    _ = query(_)
    return _


def get_geometry(store,
                 subject, lst2arr: Literal['vertices'] | Literal['transform'] | Literal['definition/vertices'],
                 branch, graph=None):
    _ = (
        subject,
        lists_selector(subject, lst2arr,),
        geo_branch_selector(branch))
    _ = geoq(*_, graph=graph)
    _ = store.query(_) # slow!!! TODO? can just cache the hull result
    if   'vertices' in lst2arr:     shape = (-1, 3)
    elif lst2arr == 'transform':    shape = (4,4)
    else:                           #shape = (-1,) # nothing. makes no sense to keep going
        raise ValueError(f"converting {lst2arr} list to array not defined")
    from collections import defaultdict
    g = defaultdict(list)
    for lst, i, xyz in _: g[lst].append(xyz)
    _ = g
    assert(_) # need to have data
    from itertools import chain
    _ = chain.from_iterable(_.values())
    _ = map(lambda _: float(_.value ), _)
    _ = tuple(_)
    from numpy import array
    _ = array(_)
    _ = _.reshape(*shape)
    return _


def in_hull(pts, hull): # -> list/array of bool
    # TODO: concave hull
    #https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl/16898636#16898636
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """
    from scipy.spatial import Delaunay
    if not isinstance(hull, Delaunay):
        hull = Delaunay(hull)
    return hull.find_simplex(pts)>=0 # test if inside



def frac_pts_in(o1: 'pts', o2: 'pts',
           isin = in_hull,
           sample=False, frac1=.1, frac2=.1,
           ) -> float:
    """fraction of pts of o1 in o2"""
    # default is the conservative/thorough setting.
    if sample: # this may not be needed here. part of Object.volume_pts functionality
        from random import sample
        #                need at least 1 pt.
        o1 = sample(o1, max(1, int(len(o1)*frac1)) )
        #                need at least 4 pts.
        o2 = sample(o2, max(4, int(len(o2)*frac2)) )
    _ = isin(o1, o2)
    _ = sum(_) / len(_)
    return _

from functools import cached_property

class Object:
    # perhaps the speckle sdk is useful here
    def __init__(self, uri, store, branch) -> None:
        uri = str(uri)
        if not (uri.startswith('<')):
            uri = '<'+uri
        if not (uri.endswith(  '>')):
            uri = uri+'>'
        self.uri = uri
        self.store = store
        self.branch = branch # reqd to filter
    
    @classmethod
    def get_objects(cls, store, category, branch):
        for uri in get_objects(store, category, branch=branch, ):
            yield cls(uri, store, branch)
    
    def __str__(self) -> str:
        return str(self.uri)
    
    def has(self, property) -> 'node':
        _ = has_property(self.store, property, subject=self.uri)
        if _: return _ # or _.value since it's wrapped
    
    def vertices(self):
        if self.has('definition',) and self.has('transform'):
            v = get_geometry(self.store, self.uri, 'definition/vertices', self.branch)
            from numpy import stack, ones
            v = stack((v[:, 0], v[:, 1], v[:, 2], ones(len(v))), axis=-1)
            v = v.reshape(len(v), 4, 1)
            t = self.transform()  # why is it 4x4 instead of 3x3?
            v = t @ v
            v = v[:, (0, 1, 2)]
            v = v.reshape(len(v), 3)
            return v
        elif self.has('displayValue'):
            return get_geometry(self.store, self.uri, 'vertices', self.branch)
        
        raise Exception('really should return vertices')
    
    def get_volume_pts(self, ): # arg: npts.
        # TODO
        # take the CONCAVE hull and 'fill it' 
        # to more generally talk about 'percent inside'
        # approach:
        # * take sets of set(p1, p2)
        #   interpolate b/w them?
        # * take the enclosing cube
        #   generate random pts in the cube
        #   check if inside hull to admit
        return self.vertices() # ...so this is not accurate
    @cached_property
    def volume_pts(self):
        return self.get_volume_pts()
    
    def transform(self,):
        if self.has('transform'):
            return get_geometry(self.store, self.uri, 'transform', self.branch)
        
    def hull(self):
        # TODO: CONVEX
        from scipy.spatial import Delaunay
        _ = Delaunay(self.vertices())
        return _
    
    def frac_inside(self, other: 'Object', **kw) -> float:
        return frac_pts_in(self.volume_pts, other.volume_pts, **kw)
        
    def __contains__(self, other: 'Object'):
        if self.frac_inside(other) == 1: # precisely. otherwise, use frac_inside
            return True
        else:
            return False

# general checking enclosing procedure:
# for some obj, get its vertices
# if the obj is has transform property 
# then the associated vertices should be transformed,
# or, as a shortcut, just the translation pt is used.
# (but then the translation pt should be in the enclosure).



from typing import Iterable
from types import SimpleNamespace as NS
class Comparison(NS): pass

def compare(store,
        cat1, cat2,
        branch1, branch2,
        analysis: Literal['fracInside'] | Literal['inside'] = 'inside', tol=.9, **kw) -> Iterable[Comparison]:
    C = Comparison
    for o1 in Object.get_objects(store, cat1, branch1):
        for o2 in Object.get_objects(store, cat2, branch2):
            if analysis == 'fracInside':
                f = o1.frac_inside(o2, **kw)
                yield                       C(o1=o1, fracInside=f,  o2=o2)
            elif analysis == 'inside':
                f = o1.frac_inside(o2, **kw)
                if f > tol: yield           C(o1=o1, inside=f,      o2=o2)
                break # no need for all
            raise ValueError('what analysis?')


# geometry above
# semantic stuff below

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


# just make one 'http://geo/fracInside'
# to expose in construct mapping


from .engine import Triples
def assigment_triples(d: dict, cat1, cat2) -> Triples:
    import pyoxigraph as og
    u = get_uri()
    if (cat1=='Lighting Fixtures') and (cat2=='Rooms'):
        _ = [og.Triple(o1, og.NamedNode(u+'hasPhysicalLocation'), o2) for o1,o2 in d.items()]
    else:
        _ = []
    _ = Triples(_)
    return _


from .engine import OxiGraph

from typing import Callable
def get_obj_assignment_rule(cat1, cat2, branch1=None, branch2=None) -> Callable[[OxiGraph], Triples]:
    # o1 contains o2
    def r(db: OxiGraph,) -> Triples:
        _ = get_obj_assignment_dict(db, cat1, cat2, branch1=branch1, branch2=branch2)
        _ = assigment_triples(_, cat1, cat2)
        return _
    return r

