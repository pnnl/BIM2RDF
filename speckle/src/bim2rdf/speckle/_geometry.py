#### not used:

class Query(str): pass

from functools import lru_cache
@lru_cache(maxsize=None)
def has_property(store, property: str|tuple, category=None, subject=None, limit=1):
    # objects in the speckle sense (not semantic)
    #no need for model and graph specifiers
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
    _ = Query(_)
    _ = store.query(_)
    _ = tuple(r[0] for r in _)
    assert(len(_) in {0, 1})
    if _: return _[0]

def from_graph(graph:str=''):
    return ('from'+graph) if graph else ''

from bim2rdf.speckle import base_uri, meta_uri

def prefixes():
    _ = f"""
    PREFIX spkl: <{base_uri()}>
    PREFIX meta: <{meta_uri()}>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    """
    return _


def objectsq(cat, model=None, graph=None):
    # objects in the speckle sense (not semantic)
    _ = f"?s spkl:category \"{cat}\""
    if model:
        bl = f"""<< {_} >> meta: <<?model spkl:name "{model}" >>."""
    else:
        bl = ''
    _ = f"""
    {prefixes()}

    select distinct ?s {from_graph(graph)}
    where {{
        {_}.
        {bl}
    }}
    """ # modelName could be used here TODO
    _ = Query(_)
    return _


def get_objects(store, cat, model=None, graph=None):
    # fast enough query
    _ = objectsq(cat, model=model, graph=graph)
    _ = store.query(_)
    return tuple(r[0] for r in _)


def geo_model_selector(model=None):
    s = f'<<?_so ?_sp ?vl >>'
    p = "meta:"
    o = f'<<?_model spkl:name "{model}" >>'  # modelName could be used here TODO
    _ = f"{s} {p} {o}." if model else ''
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
         graph=None, ) -> Query:  # add to group, the export
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
    # need model selector if have subject?
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
    #{'model_selector'} HUGE difference!!!!
    }}
    {grouping}
    """
    _ = Query(_)
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

    def faces(seq):
        # interpreted as:
        # [nVertices, v1, v2, vn, nVertices, v1, v2, ...]
        # list(
        # faces([
        #     3,    1, 1, 1,
        #     3,    2, 1, 1,
        #     5,    1 , 2 , 3 ,4 ,5,
        #     1,    111])
        # = >  [[1, 1, 1], [2, 1, 1], [1, 2, 3, 4, 5], [111]]
        nexti = 0
        for i, e in enumerate(seq):
            if nexti == i:
                n = seq[i]
                # 
                yield seq[i+1:i+1+n]
                nexti = i+1+n

    def mk_array(ls, lst2arr=list_selector):
        if   'vertices' in lst2arr:     shape = (-1, 3)
        elif 'faces'    in lst2arr:     shape = (-1, )  # interpreted as nVertices, v1, v2, vn, nVertices, v1, ...
        elif lst2arr == 'transform':    shape = ( 4, 4)
        else:                           #shape = (-1,) # nothing. makes no sense to keep going
            raise ValueError(f"converting {lst2arr} list to array not defined")
        from bim2rdf.speckle.objects import data_decode
        _ = ls; del ls
        _ = map(lambda _: data_decode(_), _)
        if 'faces' in lst2arr:
            _ = (v.astype('int') for v in _)
        _ = map(lambda _: (_).reshape(*shape), _)
        if 'faces' in lst2arr:
            _ = map(lambda l:tuple(faces(l)), _)
        _ = tuple(_) # need to pass in a 'real' sequence ..
        return _
    
    def arrays():
        from collections import defaultdict
        ptrs = defaultdict(list)
        if 'matrix' in path:
            for s,p in q:   ptrs[s].append(p)
        else:
            for s,i,p in q: ptrs[s].append(p)  #don't need i bc it's going in ordered
        #                               flattening
        from itertools import chain
        lps = get_lists_from_ptrs(store, tuple(chain.from_iterable(ptrs.values()) ) , path )
        lps = [(p,l) for (p,l) in lps]
        _ = {}
        # subject -> arrays/lists
        for k,ps in ptrs.items():
            lists = [l for (p,l) in lps if p in ps]
            _[k] = mk_array(s.value for s in lists)
        return _
    return arrays


#@'low' level. 'higher' level is in memory
#from .cache import get_cache
#def geomkey(*p, **k):
# skip the first arg bc it doesn't hash and dont want it to be part of the key
#from cachetools.keys import hashkey
#return hashkey(*p[1:], **k)
#@get_cache('geometry', key=geomkey)
@lru_cache(maxsize=None)
def category_geom_getter(store,
                 cat, lst2arr: list_selection,
                 model=None,
                 graph=None):
    os = get_objects(store, cat, model=model, graph=graph)
    _ = geometry_getter(store, os, lst2arr, graph=graph)
    from types import SimpleNamespace as NS
    _ = NS(objects=os, getter=_)
    return _


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
        return _
        
    
    @cached_property
    def vertices(self):
        vs = self.obj.get_geometry(self.obj.store, 'definition/vertices', )
        t = self.transform
        _ = tuple(self.obj.calc_vertices(v, t) for v in vs)
        return _



objects_cache = {}
class Object:
    # perhaps the speckle sdk is useful here,
    # so that i dont have to query
    def __init__(self, uri, store, model,
            geom_getter_type:Literal['single']|Literal['category']='single') -> None:
        uri = str(uri)
        if (uri.startswith('<')):
            uri = uri[1:]
        if (uri.endswith(  '>')):
            uri = uri[:-1]
        self.uri = uri
        self.store = store
        self.model = model # reqd to filter
        self.geom_getter_type = geom_getter_type
    
    def __str__(self) -> str:
        return f"<{self.uri}>"
    
    def __repr__(self) -> str:
        return f"Object({self.uri})"
    
    def __hash__(self) -> int:
        return hash(self.uri)
    
    def get_geometry(self, store, lst2arr: list_selection):
        from pyoxigraph import NamedNode
        s = NamedNode(self.uri)
        if self.geom_getter_type == 'single':
            _ = geometry_getter(store, (self,), lst2arr,)
            _ = _()
            _ = _[s]
            return _
        else:
            assert('category' == self.geom_getter_type)
            _ = self.has('category')
            _ = _.value
            _ = category_geom_getter(store, _, lst2arr, self.model, )
            _ = _.getter
            _ = _()
            _ = _[s]
            return _
        raise NotImplementedError('how to get geometry?')
    
    @classmethod
    def get_objects(cls, store, category, model, use_cache=True):
        for uri in get_objects(store, category, model=model,):
            if not use_cache:
                _ = cls(uri, store, model, geom_getter_type='category')
                yield _
            else:
                if uri in objects_cache:
                    yield objects_cache[uri]
                else:
                    _ = cls(uri, store, model, geom_getter_type='category')
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
            _ = _[0]
            assert(_.shape == (4,4) ) # why is it 4x4 instead of 3x3?
            return _

    @property #@cached_property # fast enough i'm assuming
    def vertices(self):
        if self.definition:
            _ = lambda vl: self.calc_vertices(
                            vl,
                            self.transform,)
            _ = map(_, self.definition.vertices)
            _ = tuple(_)
        elif self.has('displayValue'):
            _ = self.get_geometry(self.store, 'vertices', )
        else:
            raise Exception('really should return vertices')
        
        from numpy import vstack
        return vstack(_)
    
    #@cached_property
    @property
    def faces(self):
        if self.definition:
            fss = self.get_geometry(self.store, 'definition/faces')
        elif self.has('displayValue'):
            fss = self.get_geometry(self.store, 'faces')
        _ = {} # face->vertices
        shift = 0
        #assert(sum(fs for fs in fss) == len(self.vertices))
        for i, fs in enumerate(fss):
            vss = set()
            for f, vis in enumerate(fs):
                f = (i, f)
                _[f] = vis + shift
                vss.update(vis)
                #_[f] = vss[i][vis] # to get at the data
            shift += max(vss)+1 # *sigh*        
        return _
    

