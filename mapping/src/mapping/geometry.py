
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
    s = subject
    #                 displayValue -->   List -->         Vertices -->     List -->      base64data --> str
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


def geo_branch_selector(branch=None):
    s = f'<<?_so ?_sp ?vl >>'
    p = "meta:"
    o = f'<<?_branch spkl:name "{branch}" >>'  # branchName could be used here TODO
    _ = f"{s} {p} {o}." if branch else ''
    return _


def geoq(subject, list_selector, branch_selector='', graph=None, ) -> query:  # add to group, the export
    # single object at a time to not load all geometry in one query
    # using values seems to help with performance. (using filter was too slow)
    # need branch selector if have subject?
    _ = f"""
    {prefixes()}

    select ?vl  {from_graph(graph)}
    where {{
    values ?s {{ {subject} }}
    {list_selector}
    {branch_selector}
    }}
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
    elif lst2arr == 'transform':    shape = ( 4, 4)
    else:                           #shape = (-1,) # nothing. makes no sense to keep going
        raise ValueError(f"converting {lst2arr} list to array not defined")
    from collections import defaultdict
    g = defaultdict(list)
    for i,lst in enumerate(_): g[i].append(lst[0].value)
    _ = g
    assert(_) # need to have data
    from itertools import chain
    _ = chain.from_iterable(_.values())
    from speckle.objects import data_decode
    _ = map(lambda _: data_decode(_), _)
    _ = map(lambda _: (_).reshape(*shape), _)
    from numpy import vstack
    _ = tuple(_) # need to pass in a 'real' sequence ..
    _ = vstack(_) # ...bc this gives a FutureWarning
    return _


def in_hull(pts, hull): # -> list/array of bool
    #https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl/16898636#16898636
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """
    return hull.find_simplex(pts)>=0 # test if inside
# general checking enclosing procedure:
# for some obj, get its vertices
# if the obj is has transform property 
# then the associated vertices should be transformed,
# or, as a shortcut, just the translation pt is used.
# (but then the translation pt should be in the enclosure).

def hull(pts):
    # TODO: concave hull
    from scipy.spatial import Delaunay
    return Delaunay(pts)


objects_cache = {} # TODO: could set an item limit

from functools import cached_property
class Object:
    # perhaps the speckle sdk is useful here,
    # so that i dont have to query
    def __init__(self, uri, store, branch) -> None:
        uri = str(uri)
        if not (uri.startswith('<')):
            uri = '<'+uri
        if not (uri.endswith(  '>')):
            uri = uri+'>'
        self.uri = uri
        self.store = store
        self.branch = branch # reqd to filter
    
    def __repr__(self) -> str:
        return f"Object({self.uri})"
    
    def __hash__(self) -> int:
        return hash(self.uri)
    
    @classmethod
    def get_objects(cls, store, category, branch):
        for uri in get_objects(store, category, branch=branch, ):
            if uri in objects_cache:
                yield objects_cache[uri]
            else:
                _ = cls(uri, store, branch)
                objects_cache[uri] = _
                yield _

    
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
            t = self.transform  # why is it 4x4 instead of 3x3?
            v = t @ v
            v = v[:, (0, 1, 2)]
            v = v.reshape(len(v), 3)
            return v
        elif self.has('displayValue'):
            return get_geometry(self.store, self.uri, 'vertices', self.branch)
        
        raise Exception('really should return vertices')
    
    def get_volume_pts(self, n = 100, seed=123):
        # generate random pts in hull
        _ = self.vertices()
        from numpy import array
        bounds = array([_.min(axis=0), _.max(axis=0)]).T
        assert(bounds.shape == (3,2))
        import numpy.random as random
        r = random.default_rng(seed) # need a seed for deterministic,
        # ...otherwise process will keep generating (new) data
        pts = (
            r.uniform(*bounds[0], n*2), # double is more than good
            r.uniform(*bounds[1], n*2),
            r.uniform(*bounds[2], n*2))
        del bounds
        pts = array(pts)
        pts = pts.T
        assert(pts.shape[1] == 3)
        _ = in_hull(pts, self.hull)
        _ = pts[_][:n] # filtering Trues
        assert(_.shape[0] == n)  # very unlikely to fail
        return _
    @cached_property
    def volume_pts(self): return self.get_volume_pts()
    
    def get_transform(self,):
        if self.has('transform'):
            return get_geometry(self.store, self.uri, 'transform', self.branch)
    @cached_property
    def transform(self): return self.get_transform()
    @cached_property
    def hull(self):
        _ = hull(self.vertices())
        return _
    
    def frac_inside(self, other: 'Object', **kw) -> float:
        _ = in_hull(self.volume_pts, other.hull, **kw)
        _ = sum(_) / len(_)
        return _
        
    def __contains__(self, other: 'Object'):
        if other.frac_inside(self) == 1: # precisely. otherwise, use frac_inside
            return True
        else:
            return False



from typing import Iterable
def compare(store: 'og.Store',
        cat1, cat2,
        branch1, branch2,
        analysis: Literal['fracInside'] | Literal['inside'] = 'inside', tol=.9, ) -> Iterable['Comparison']:
    C = Comparison
    for o1 in Object.get_objects(store, cat1, branch1):
        for o2 in Object.get_objects(store, cat2, branch2):
            if analysis == 'fracInside':
                f = o1.frac_inside(o2)
                yield                       C(o1, f, o2)
                continue
            elif analysis == 'inside':
                f = o1.frac_inside(o2)
                if f > tol:
                    # found its (1) location...
                    yield                   C(o1, f, o2)
                    break # ...no need to go through the rest.
                else:
                    continue
            raise ValueError('what analysis?')


# geometry above

class Comparison:
    uri = 'http://mapping/geo#'#fracInside'
    def __init__(self, o1: Object, fracInside, o2: Object) -> None:
        self.o1 = o1
        self.fracInside = fracInside
        self.o2 = o2

    def triples(self) -> 'Triples':
        # map these triples to ontology in a sparql construct 
        from pyoxigraph import parse
        _ = f"""
        PREFIX geo: <{self.uri}>
        {self.o1.uri} geo:fracInside [
                        {self.o2.uri}  {self.fracInside}  ].
        """
        _ = _.encode()
        from io import BytesIO
        _ = parse(BytesIO(_), 'text/turtle')
        _ = tuple(_)
        return _


# semantic stuff below


from .engine import OxiGraph, Triples
def locations(db: OxiGraph) -> Triples:
    branch = 'architecture/rooms and lighting fixtures'
    for c in compare(db._store, 'Lighting Fixtures', 'Rooms', branch, branch, analysis='inside'):
        yield from c.triples()
    # add more: space, zone, room stuff
