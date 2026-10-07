
class _SpeckleGetter:
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

    @property
    def json(self, ):
        return self.version.json()

    @property
    def rule(self):
        from rdf_rules.data.json import JSON
        class SpeckleGetter(JSON): pass
        return SpeckleGetter(lambda: self.data,
            additional_params={
                'model_name':self.model.name,
                'version': self.version.id } )


from rdf_rules.data.json import JSON
class SpeckleGetter(JSON):
    def __init__(self, *, project_id, version_id):
        sg = _SpeckleGetter(project_id=project_id, version_id=version_id)
        j = sg.json.data
        super().__init__(j)

    @classmethod
    def from_names(cls, *, project, model):
        _ = _SpeckleGetter.from_names(project=project, model=model)
        _ = cls(project_id=_.project_id, version_id=_.version_id)
        return _

# from typing import Callable
# def ttl(self, *, json_method:str|Callable=Json.wo_geometry, **kw):
#     from .meta import prefixes
#     dp = prefixes.data(project_id=self.model.project.id, object_id="") # objid filled in
#     _ = self.json()
#     _ = getattr(_, json_method.__name__ if not isinstance(json_method, str) else json_method) # ?
#     _ = _()
#     _ = json2rdf(_,
#             subject_id_keys=('_id', 'id',),     object_id_keys=('referencedId', 'connectedConnectorIds'),
#             id_prefix=(str(dp.name), str(dp.uri)),
#             key_prefix=(str(prefixes.concept.name), str(prefixes.concept.uri)),
#             deanon=True,
#             **kw)
#     return _
