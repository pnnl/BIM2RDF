
class _SpeckleGetters:
    def __init__(self, *, project_id, version_id, geometry=False):
        self.project_id = project_id
        self.version_id = version_id
        self.geometry =geometry
        
    @classmethod
    def from_names(cls, *, project, model, geometry=False):
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
        return cls(project_id=p.id, version_id=v.id, geometry=geometry)

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
    def tables(self):
        for n, df in self.version.parquets.items():
            if not self.geometry:
                if 'geometries' in n:
                    continue
            yield n, df


from rdf_rules.data.table import Table
class SpeckleGetter(Table):
    def __init__(self, df,  *,  version_id, model_name,  table_name, ):
        name = f"{model_name}/{table_name}"
        super().__init__(df,  name=name, additional_params={
            'version_id':version_id,
        })

    @classmethod
    def s(cls, *, project_id, version_id, geometry=False):
        sgs = _SpeckleGetters(project_id=project_id, version_id=version_id, geometry=geometry)
        for n, df in sgs.tables:
            yield cls(df,  version_id=version_id, model_name=sgs.model.name, table_name=n)

    @classmethod
    def from_names(cls, *, project, model, geometry=False):
        sgs = _SpeckleGetters.from_names(project=project, model=model, geometry=geometry)
        for n, df in sgs.tables:
            yield cls(df, version_id=sgs.version_id, model_name=sgs.model.name, table_name=n)
