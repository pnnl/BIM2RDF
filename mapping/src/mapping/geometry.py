
class query(str): pass

from functools import lru_cache
@lru_cache(maxsize=None)
def has_property(store, property: str|tuple, category=None, subject=None, limit=1):
    # objects in the speckle sense (not semantic)
    #no need for branch and graph specifiers
    if isinstance(property, str):
        property = f"spkl:{property}"
    else:
        assert(isinstance(property, tuple))
        property = '/'.join(f"spkl:{p}" for p in property)
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
        {subject} {property} ?v.
        {categoryline}
    }}
    limit {limit}
    """
    _ = query(_)
    _ = store.query(_)
    _ = tuple(r[0] for r in _)
    assert(len(_) in {0, 1})
    if _: return _[0]

def from_graph(graph:str=''):
    return ('from'+graph) if graph else ''

from speckle import base_uri, meta_uri

def prefixes():
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX meta: <{meta_uri()}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
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


def list_selector_lines():
    from types import SimpleNamespace as NS
    displayValue = NS(
        # subject -> displayValueS
        dvs = lambda s, d: f"{s} {'spkl:definition/' if d else ''}spkl:displayValue ?dvl.",
        # just for counting
        ctr = lambda : f'?dvl rdf:rest* ?mid. ?mid rdf:rest* ?_.',
        # displayValue
        dv = lambda : f'?_ rdf:first ?dv.',
        # dv to the data list. p is for vertices|faces, d is for data
        l = lambda p, d: f"?dv spkl:{p}/rdf:rest*/rdf:first{'/spkl:data' if d else ''} ?l.")
    def transform(s, p):
        return f"{s} spkl:transform{'/spkl:matrix' if p else ''} ?l."
    return NS(displayValue=displayValue, transform=transform)


from typing import Literal
def geoq(subjects: str|tuple,
         list_selector: (
            Literal['vertices'] | Literal['definition/vertices'] 
            | Literal['faces'] | Literal['definition/faces']
            | Literal['transform'],  ),
        data: bool,
         graph=None, ) -> query:  # add to group, the export
    # https://stackoverflow.com/questions/17523804/is-it-possible-to-get-the-position-of-an-element-in-an-rdf-collection-in-sparql
    # prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # select ?element (count(?mid)-1 as ?position) where { 
    # [] :list/rdf:rest* ?mid . ?mid rdf:rest* ?node .
    # ?node rdf:first ?element .
    # }
    # group by ?node ?element
    if isinstance(subjects, str):
        subjects = (subjects,)
    else:
        assert(isinstance(subjects, (tuple, list, frozenset, set)))
    # single object at a time to not load all geometry in one query
    # using values seems to help with performance. (using filter was too slow)
    # need branch selector if have subject?
    if 'transform' == list_selector:
        select = f"select distinct ?s ?l"
        lines = list_selector_lines().transform
        lines = (
            lines('?s', data),
        )
        grouping = ''
    else:
        assert(('vertices' in list_selector) or ('faces' in list_selector) )
        select = f"select distinct ?s (count(?mid)-1 as ?i ) ?l {from_graph(graph)}"
        lines = list_selector_lines().displayValue
        lines = (
            lines.dvs('?s', True if 'definition' in list_selector else False),
            lines.ctr(),
            lines.dv(),
            lines.l('faces' if 'faces' in list_selector else 'vertices', data) )
        grouping = f"group by ?s ?dvl ?dv ?l \n order by ?s ?i"
    _ = f"""
    {prefixes()}
    {select}
    where {{
    values ?s {{ {' '.join(str(s) for s in subjects)} }}
    {' '.join(lines)}
    #{'branch_selector'} HUGE difference!!!!
    }}
    {grouping}
    """
    _ = query(_)
    return _

list_selection = (
    Literal['vertices'] | Literal['definition/vertices'] 
    | Literal['faces'] | Literal['definition/faces']
    | Literal['transform'],  )
def query_geometry(store,
        subjects,
        list_selector: list_selection,
        data:bool, 
        graph=None):
    _ = geoq(subjects, list_selector, data=data, graph=graph)
    _ = store.query(_) # FAST!.
    # _ = tuple(_) query returns non-evaluated iter
    return _

def get_lists_from_ptrs(store, ptrs, path):
    if not isinstance(ptrs, (tuple, list, set, frozenset)):
        ptrs = (ptrs, )
    _ = f"""
    {prefixes()}

    select ?vlp ?vl
    where {{
        values ?vlp {{{' '.join(str(p) for p in ptrs)}}}.
        ?vlp {path} ?vl.
        filter(datatype(?vl)=xsd:string ) # idk why had to put this 
    }}
    """
    _ = store.query(_)
    return _


def geometry_getter(store,
        subjects: tuple,
        list_selector: list_selection,
         graph=None):
    # multiple subjects: means array data can be retrieved and held at once.
    # data storage: subject --> array ptr --> array
    # more efficient than subject --> array bc geometries may be repeated in the definition/vertices case
    q = query_geometry(store, subjects, list_selector, False, graph=graph)
    if any(w in list_selector for w in {'vertices', 'faces'}):
        path = 'data'
    else:
        assert('transform' in list_selector)
        path = 'matrix'
    path = f"spkl:{path}"

    def mk_array(ls, lst2arr=list_selector):
        if   'vertices' in lst2arr:     shape = (-1, 3)
        elif 'faces'    in lst2arr:     shape = (-1,  )  # nothing
        elif lst2arr == 'transform':    shape = ( 4, 4)
        else:                           #shape = (-1,) # nothing. makes no sense to keep going
            raise ValueError(f"converting {lst2arr} list to array not defined")
        from speckle.objects import data_decode
        _ = ls; del ls
        _ = map(lambda _: data_decode(_), _)
        if 'faces' in lst2arr:
            _ = (v.astype('int') for v in _)
        _ = map(lambda _: (_).reshape(*shape), _)
        _ = tuple(_)
        return _
        from numpy import vstack
        _ = tuple(_) # need to pass in a 'real' sequence ..
        _ = vstack(_) # ...bc this gives a FutureWarning
        return _
    
    def arrays():
        from collections import defaultdict
        ptrs = defaultdict(list)
        if 'matrix' in path:
            for s,p in q:   ptrs[s].append(p)
        else:
            for s,i,p in q: ptrs[s].append(p)  #don't need i bc it's going in ordered
        # a copy to get rid of dd
        # need KeyError
        ptrs = {k:v for k,v in ptrs.items()}
        _ = get_lists_from_ptrs(store, tuple(p for pl in ptrs.values() for p in pl) , path )
        lists = defaultdict(list)
        for p,l in _: lists[p].append(l)
        lists = {k:mk_array(s.value for s in v) for k,v in lists.items()}
        return lists
    return arrays()
    

    def get_array(subject, ):#ptrs=ptrs, lists=lists):
        _ = get_lists(subject,)# ptrs=ptrs, lists=lists)
        _ = mk_array(_)
        return _
    return get_array


#@'low' level. 'higher' level is in memory
#from .cache import get_cache
#def geomkey(*p, **k):
# skip the first arg bc it doesn't hash and dont want it to be part of the key
#from cachetools.keys import hashkey
#return hashkey(*p[1:], **k)
#@get_cache('geometry', key=geomkey)
@lru_cache(maxsize=None)
def category_geom_getter(store,
                 cat, lst2arr: Literal['vertices'] | Literal['transform'] | Literal['definition/vertices'],
                 branch=None,
                 graph=None):
    os = get_objects(store, cat, branch=branch, graph=graph)
    _ = geometry_getter(store, os, lst2arr, graph=graph)
    from types import SimpleNamespace as NS
    _ = NS(objects=os, getter=_)
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


from functools import cached_property

class Definition:
    def __init__(self, uri, obj: 'Object' ) -> None:
        assert(uri)
        self.uri = uri
        self.obj = obj
    

    @cached_property
    def transform(self):
        # reset 'object' transform
        _ = self.obj.get_geometry(self.obj.store, 'transform', )
        assert(_.shape == (4,4) ) # why is it 4x4 instead of 3x3?
        _ = _.copy()
        _[:3, -1] = 0 # zero the translation
        return _
    
    @cached_property
    def vertices(self):
        v = self.obj.get_geometry(self.obj.store, 'definition/vertices', )
        t = self.transform
        _ = self.obj.calc_vertices(v, t)
        return _
    @cached_property
    def downsampled_vertices(self):
        return self.obj.downsample(self.vertices)

    
    def get_volume_pts(self, n = 100, xn=3, seed=123):
        return self.obj.calc_volume_pts(self.vertices, self.hull, n=n, xn=xn, seed=seed)
    @cached_property
    def volume_pts(self): return self.get_volume_pts()

    @cached_property
    def hull(self):
        _ = self.downsampled_vertices
        if _ is None: _ = self.vertices
        _ = hull(_)
        return _

    #def translate(self, object):


objects_cache = {}
class Object:
    # perhaps the speckle sdk is useful here,
    # so that i dont have to query
    def __init__(self, uri, store, branch,
            geom_getter_type:Literal['single']|Literal['category']='single') -> None:
        uri = str(uri)
        if (uri.startswith('<')):
            uri = uri[1:]
        if (uri.endswith(  '>')):
            uri = uri[:-1]
        self.uri = uri
        self.store = store
        self.branch = branch # reqd to filter
        self.geom_getter_type = geom_getter_type
    
    def __str__(self) -> str:
        return f"<{self.uri}>"
    
    def __repr__(self) -> str:
        return f"Object({self.uri})"
    
    def __hash__(self) -> int:
        return hash(self.uri)
    
    def get_geometry(self, store, lst2arr):
        from pyoxigraph import NamedNode
        s = NamedNode(self.uri)
        if self.geom_getter_type == 'single':
            _ = geometry_getter(store, (self,), lst2arr,  )
            _ = _(s)
            return _
        else:
            assert('category' == self.geom_getter_type)
            _ = self.has('category')
            _ = _.value
            _ = category_geom_getter(store, _, lst2arr, self.branch, )
            _ = _.getter
            _ = _(s)
            return _
        raise NotImplementedError('how to get geometry?')
    
    @classmethod
    def get_objects(cls, store, category, branch, use_cache=True):
        for uri in get_objects(store, category, branch=branch,):
            if not use_cache:
                _ = cls(uri, store, branch, geom_getter_type='category')
                yield _
            else:
                if uri in objects_cache:
                    yield objects_cache[uri]
                else:
                    _ = cls(uri, store, branch, geom_getter_type='category')
                    objects_cache[uri] = _
                    yield _
    
    def has(self, property) -> 'node':
        _ = has_property(self.store, property, subject=self)
        if _: return _ # or _.value since it's wrapped
    
    @property
    def definition(self) -> 'Definition | None':
        cls = self.__class__
        if not hasattr(cls, 'definitions'): cls.defs = {}
        d = self.has('definition')
        if d is None: return
        if d not in cls.defs:
            cls.defs[d] = Definition(d, self)
        return cls.defs[d]

    @staticmethod
    def downsample(vertices, seed=123, toomuch=10_000):
        _ = vertices
        if len(_) > toomuch:
            import numpy.random as random
            r = random.default_rng(seed) # need a seed for deterministic,
            r = r.integers(0, len(_), toomuch)
            _ = _[r]
            return _
    
    @staticmethod
    def calc_vertices(v, t):
        from numpy import stack, ones
        #                                    need to put in a 1 col to be compatible with t @ v
        v = stack((v[:, 0], v[:, 1], v[:, 2], ones(len(v))), axis=-1)
        v = v.reshape(len(v), 4, 1)
        v = t @ v
        v = v[:, (0, 1, 2)]
        v = v.reshape(len(v), 3)
        return v
    
    @cached_property
    def translation(self):
        _ = self.transform
        return _[:3, -1] 

    @cached_property
    def transform(self):
        if self.definition:
            _ = self.get_geometry(self.store, 'transform', )
            assert(_.shape == (4,4) ) # why is it 4x4 instead of 3x3?
            return _

    @property #@cached_property # fast enough i'm assuming
    def vertices(self):
        if self.definition:
            _ = self.calc_vertices(
                    self.definition.vertices,
                    self.transform,)
            return _
        elif self.has('displayValue'):
            return self.get_geometry(self.store, 'vertices', )
        
        raise Exception('really should return vertices')
    
    @property
    def faces(self):
        if self.definition:
            return self.get_geometry(self.store, 'definition/faces')
        elif self.has('displayValue'):
            return self.get_geometry(self.store, 'faces')

    @staticmethod
    def calc_volume_pts(vertices, hull, n = 100, xn=3, seed=123):
        # generate random pts in hull
        _ = vertices
        from numpy import array
        bounds = array([_.min(axis=0), _.max(axis=0)]).T
        assert(bounds.shape == (3,2))
        import numpy.random as random
        r = random.default_rng(seed) # need a seed for deterministic,
        # ...otherwise process will keep generating (new) data
        pts = (
            r.uniform(*bounds[0], n*xn), # 
            r.uniform(*bounds[1], n*xn),
            r.uniform(*bounds[2], n*xn))
        del bounds
        pts = array(pts)
        pts = pts.T
        assert(pts.shape[1] == 3)
        _ = in_hull(pts, hull)
        _ = pts[_][:n] # filtering Trues
        assert(_.shape[0] == n)  # very unlikely to fail. but more likely for non-boxy objects.
        return _
    
    def get_volume_pts(self, n = 100, xn=3, seed=123):
        if self.definition:
            _ = self.definition.volume_pts
            _ = _ + self.translation
            return _
        else:
            return self.calc_volume_pts(self.vertices, self.hull, n=n, xn=xn, seed=seed)
    @cached_property
    def volume_pts(self): return self.get_volume_pts()

    @cached_property
    def hull(self):
        if not self.definition:
            _ = self.downsample(self.vertices)
            if _ is None: _ = self.vertices
            _ = hull(_)
            return _
    
    def frac_inside(self, other: 'Object', **kw) -> float:
        if other.definition:#.hull:
            # translate to hull
            v = self.volume_pts - self.translation # plus or minus? i think minus bc o1.frac_inside(o1)=>1
            _ = in_hull(v, other.definition.hull, **kw)
        else:
            assert(other.hull is not None)
            _ = in_hull(self.volume_pts, other.hull)
        _ = sum(_) / len(_)
        return _
    
    @cached_property
    def med_pt(self):
        # a shortcut
        if self.transform  is not None:
           return self.transform[:,-1][:3]
        from numpy import median
        return median(self.vertices, axis=0)

    def med_distance(self, other):
        sp = self.med_pt
        op = other.med_pt
        _ = ((sp[i]-op[i])**2 for i in range(3))
        _ = sum(_)
        _ = _**.5
        return _
        
    def __contains__(self, other: 'Object'):
        if other.frac_inside(self) == 1: # precisely. otherwise, use frac_inside
            return True
        else:
            return False


def calc_distances(o1s, o2s):
    for o1 in o1s:
        for o2 in o2s:
            yield frozenset((o1, o2)), lambda: o1.med_distance(o2)


distances = {}

from typing import Iterable
def compare(store: 'og.Store',
        cat1, cat2,
        branch1, branch2,
        analysis:Literal['fracInside']='fracInside', top=10, tol=.1 ) -> Iterable['Comparison']:
    C = Comparison
    from tqdm import tqdm
    o1s = Object.get_objects(store, cat1, branch1)
    o1s = tuple(o1s)
    o2s = Object.get_objects(store, cat2, branch2)
    o2s = tuple(o2s)
    
    ### optimization for when we're looking for the 'location' of things.
    # can be 'smarter'
    if analysis == 'fracInside':
        def ddistances():
            for p,df in calc_distances(o1s, o2s):#, pretty fast. doesnt need progress bar total=len(o1s)*len(o2s), desc='distances'):
                if p not in distances:
                    distances[p] = df()
        ddistances()
        
    def sorter(o1, o2s):
        if analysis == 'fracInside':
            return sorted(o2s, key=lambda o2: distances[frozenset((o1, o2))] )[:top] # is enough
        else:
            raise ValueError('whats the analysis?')
    ###
        
    for i, o1 in enumerate(tqdm(o1s, desc=f"{cat1}-{cat2}")):
        for j, o2 in enumerate(sorter(o1, o2s)):
            yield C(o1, 'distanceRank', j, o2)
            if analysis == 'fracInside':
                f = o1.frac_inside(o2)
                if f>tol: yield C(o1, 'fracInside', f, o2)
                continue
            raise ValueError('what analysis?')

# geometry above

geometry_uri = 'http://mapping/geo#'#fracInside'

def namespaces():
    return [
        Comparison.ns
    ]

class Comparison:
    from ontologies import namespace
    from rdflib import URIRef
    ns = namespace('geom', URIRef(geometry_uri))
    def __init__(self, o1: Object, name, fig, o2: Object) -> None:
        self.o1 = o1
        self.name = name
        self.fig = fig
        self.o2 = o2

    def triples(self) -> 'Triples':
        # map these triples to ontology in a sparql construct 
        from pyoxigraph import parse
        _ = f"""
        PREFIX {self.ns.prefix}: <{self.ns.uri}>
        {self.o1} geom:{self.name} [
                        {self.o2}  {self.fig}  ].
        """
        _ = _.encode()
        from io import BytesIO
        _ = parse(BytesIO(_), 'text/turtle')
        _ = tuple(_)
        return _


# semantic stuff below

from .engine import OxiGraph, Triples
def overlap(db: OxiGraph) -> Triples:
    #import heartrate; heartrate.trace(browser=True)
    branch = 'architecture/rooms and lighting fixtures'
    from itertools import product
    combos = product({'Lighting Fixtures', }, {'Rooms', 'Spaces'}, {branch}  )
    for o1s, o2s, b in combos:
        for c in compare(db._store, o1s, o2s, b, b, analysis='fracInside'):
            yield from c.triples()
