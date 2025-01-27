from pyoxigraph import Store, Quad, Triple, NamedNode
from typing import Iterable

from rdf_engine.rules import Rule
from bim2rdf.rdf import Prefix
class Rule(Rule):
    meta_prefix =    Prefix('meta',    'urn:meta:bim2rdf:')    # https://www.iana.org/assignments/urn-formal/meta legit!
    # shouldn need bc <<data >>  meta:key literal(value).
    _metaid_prefix =  Prefix('meta.id', 'urn:meta:id:') # https://www.iana.org/assignments/urn-formal/meta legit!
    # for subclasses
    spec: dict
    def spec_base(self):
        return {'source': self.__class__.__name__}

    @classmethod
    def repr(cls, **kw):
        nm = cls.__name__
        kw = {k:v for k,v in kw.items()
            # dont need to repr this
            if k not in {'source'} }
        from types import SimpleNamespace as NS
        _ = repr(NS(**kw)).replace('namespace', nm)
        return _
    def __repr__(self):
        return self.repr(**self.spec)
    
    from functools import cache, cached_property
    @cached_property
    def meta(self) -> tuple[Triple]: # NOT a function of data
        from json2rdf import j2r
        from boltons.iterutils import remap
        def json(p,k,v):
            err = ValueError(f'only simple key:value meta data allowed. got {repr({k:v})} ')
            if not isinstance(v, (list, dict)):
                if not isinstance(v, (bool, str, float, int, type(None) )):
                    return k, str(v) # coerce to str
            else: raise err
            if not isinstance(k, str): raise err
            return k,v
        _ = remap(self.spec, visit=json)
        _ = j2r(_,
                id_prefix=  (self._metaid_prefix.name, self._metaid_prefix.uri),
                key_prefix= (self.meta_prefix   .name, self.meta_prefix.   uri),
                )
        from pyoxigraph import parse, RdfFormat
        _ = parse(_, format=RdfFormat.TURTLE)
        _ = (q.triple for q in _)
        return tuple(_)

    def data(self, db: Store) -> Iterable[Triple]:
        #yield from [] # be nice ?
        raise NotImplementedError

    def meta_and_data(self, db: Store) ->Iterable[Quad]:
        _ = (self.data(db))           #
        #_ = (Quad(*t) for t in _)    #
        #yield from _                 # can do without 'regular' triples?
        for d in _:
            for m in self.meta:
                assert(isinstance(d, Triple))
                yield Quad(d, # nesting triple
                           # no need for m.'id' bc simple as possible
                           m.predicate, m.object) # ... and just have "meta" triples?
        # alt.
        # data triple: (s, p, o).
        # meta triple: (s, mp, mo).
        # List all metadata for the given reference to a statement
        # SELECT *
        # WHERE {
        #     <<:man :hasSpouse :woman>> ?p ?o
        # }
    def __call__(self, db): yield from self.meta_and_data(db)


class SpeckleGetter(Rule):
    meta_prefix =    Prefix('spkl.meta',    'urn:meta:speckle:')    # https://www.iana.org/assignments/urn-formal/meta legit!
    def __init__(self, *, project_id, version_id):
        self.project_id = project_id
        self.version_id = version_id
    
    @classmethod
    def from_names(cls, *, project, model):
        from speckle.data import Project
        p = [p for p in cls.projects() if p.name == project]
        assert(len(p) == 1)
        p: Project = p[0]
        m = [m for m in p.models if m.name == model]
        assert(len(m) == 1)
        m = m[0]
        assert(m.versions)
        v = sorted(m.versions, key=lambda m: m.meta['createdAt'])
        v = list(reversed(v))
        v = v[0]
        return cls(project_id=p.id, version_id=v.id)

    from speckle.data import Project, Model
    from functools import cache
    @classmethod
    @cache
    def projects(cls) -> list[Project]:
        return list(cls.Project.s())
    
    from functools import cached_property
    @cached_property
    def project(self) ->Project:
        from speckle.data import Project
        p = [p for p in self.projects() if p.id == self.project_id]
        assert(len(p) == 1)
        p: Project = p[0]
        return p
    @cached_property
    def model(self):
        for m in self.project.models:
            for v in m.versions:
                if v.id == self.version_id:
                    return m
        assert(not True)
    @cached_property
    def version(self) -> Model.Version:
        for m in self.project.models:
            for v in m.versions:
                if v.id == self.version_id:
                    return v
        assert(not True)
    
    def __repr__(self):
        _ = {#'project': self.project.name,
            'model_name': self.model.name,
             'version': self.version.id,
             **self.spec_base()}
        _ = self.repr(**_)
        return _
    
    @cached_property
    def spec(self):
        _ = {#'project': self.project.name,
             'model_name': self.model.name,
             **self.spec_base()}
        return _
    
    def data(self, db: Store):
        _ = self.version.ttl()
        from pyoxigraph import parse, RdfFormat
        _ = parse(_, format=RdfFormat.TURTLE)
        _ = (q.triple for q in _)
        yield from _





class ConstructQuery(Rule):
    def __init__(self, query: str, *, name=None):
        assert('construct' in query.lower())
        self.query = query
        self.name = name
    from pathlib import Path
    @classmethod
    def from_path(cls, p: Path):
        _ = cls(open(p).read(), name=p.name)  #idk if name will be unique enough
        _.path = p
        return _
    
    from functools import cached_property
    @cached_property
    def spec(self):
        _ = {'name': self.name, **self.spec_base()}
        if hasattr(self, 'path'):
            _['path'] = str(self.path)
        return _

    def data(self, db: Store):
        _ =  db.query(str(self.query),)
        from pyoxigraph import QueryTriples
        assert(isinstance(_, QueryTriples))
        yield from _
# need to create MappingConstructQuery(source, target)? 




#class TTLGetter

# class PyRule(Rule): need this?
