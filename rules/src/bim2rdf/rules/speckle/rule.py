from ..rule import Rule, Store

class SpeckleGetter(Rule):
    from bim2rdf.speckle.meta import prefixes
    meta_prefix = prefixes.meta
    def __init__(self, *, project_id, version_id):
        self.project_id = project_id
        self.version_id = version_id
        
    @classmethod
    def from_names(cls, *, project, model):
        from bim2rdf.speckle.data import Project
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

    from bim2rdf.speckle.data import Project, Model
    from functools import cache
    @classmethod
    @cache
    def projects(cls) -> list[Project]:
        return list(cls.Project.s())
    
    from functools import cached_property
    @cached_property
    def project(self) ->Project:
        from bim2rdf.speckle.data import Project
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
             'version': self.version.id,}
        _ = self.repr(**_)
        return _
    
    @cached_property
    def spec(self):
        _ = {#'project': self.project.name,
             'model_name': self.model.name, }
        return _
    
    def data(self, db: Store):
        _ = self.version.ttl()
        _ = _+'\n' # https://github.com/oxigraph/oxigraph/issues/1164
        from pyoxigraph import parse, RdfFormat
        _ = parse(_, format=RdfFormat.TURTLE)
        _ = (q.triple for q in _)
        yield from _
