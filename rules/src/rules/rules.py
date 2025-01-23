from pyoxigraph import Store, Quad, Triple, NamedNode

from bim2rdf.rdf import Prefix
meta =    Prefix('meta',    'urn:meta:')    # https://www.iana.org/assignments/urn-formal/meta legit!
meta_id = Prefix('meta.id', 'urn:meta:id:') # https://www.iana.org/assignments/urn-formal/meta legit!
from rdf_engine.rules import Rule
class Rule(Rule):
    meta_uri = NamedNode(str(meta.uri))
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
            if not isinstance(v, (list, dict)):
                if not isinstance(v, (bool, str, float, int, type(None) )):
                    return k, str(v) # coerce to str
            return k,v
        _ = remap(self.spec, visit=json)
        _ = j2r(_,
                id_prefix=  str(meta_id .prefix),
                key_prefix= str(meta    .prefix),
                )
        from pyoxigraph import parse
        _ = parse(_,)
        _ = (q.triple for q in _)
        return tuple(_)

    def __call__(self, db: Store):
        _ = tuple(self.data(db))                # 
        yield from _                            # can do without 'regular' triples?
        for d in _:
            for m in self.meta:
                yield Quad(d, self.meta_uri, m) # ... and just have "meta-d" triples?
        # alt.
        # data triple: (s, p, o).
        # meta triple: (s, mp, mo).
        # List all metadata for the given reference to a statement
        # SELECT *
        # WHERE {
        #     <<:man :hasSpouse :woman>> ?p ?o
        # }

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

class SpeckleGetter(Rule):
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
            'model': self.model.name,
             'version': self.version.id,
             **self.spec_base()}
        _ = self.repr(**_)
        return _
    
    @cached_property
    def spec(self):
        _ = {#'project': self.project.name,
             'model': self.model.name,
             **self.spec_base()}
        return _
    
    def data(self, db: Store):
        _ = self.version.ttl()
        from pyoxigraph import parse, RdfFormat
        _ = parse(_, format=RdfFormat.TURTLE)
        _ = (q.triple for q in _)
        yield from _

#class TTLGetter

# class PyRule(Rule): need this?