
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

    def parquet_list(self):
        for n in self.version.parquet_list():
            if not self.geometry:
                if 'geometries' in n:
                    continue
            yield n

    def table(self, name):
        return self.version.table(name)


from rdf_rules.data.table import Table
class SpeckleData(Table):
    id_col = '_hash'
    def __init__(self, df,  *,  version_id, model_name,  table_name, ):
        from bim2rdf.speckle.meta import prefixes
        *_, table_name , _dotparquet = table_name.split('.')
        super().__init__(
            lambda : self._add_meta(df, {'version_id': version_id, 'model_name': model_name }),
            name=f"{model_name}/{table_name}", 
            data_prefix=    str(prefixes.data(name=table_name).uri),
            data_id_prefix= str(prefixes.data(name=table_name).uri)+'id:',
            json2rdf_options = {'subject_id_keys':(self.id_col,)},
            additional_params={
                'version_id': version_id,
            })


    @classmethod
    def _add_meta(cls, df, meta: dict):
        df = df() if callable(df) else df
        from pandas.util import hash_pandas_object
        _ = hash_pandas_object(df, index=False)
        df[cls.id_col] = _
        for k,v in meta.items(): df[f"_{k}"] = v
        return df

    @classmethod
    def s(cls, *, project_id, version_id, geometry=False):
        sgs = _SpeckleGetters(project_id=project_id, version_id=version_id, geometry=geometry)
        for n in sgs.parquet_list():
            def gettbl(n=n): return sgs.table(n)
            yield cls(gettbl,  version_id=version_id, model_name=sgs.model.name, table_name=n)

    @classmethod
    def from_names(cls, *, project, model, geometry=False):
        sgs = _SpeckleGetters.from_names(project=project, model=model, geometry=geometry)
        for n in sgs.parquet_list():
            def gettbl(n=n): return sgs.table(n)
            yield cls(gettbl, version_id=sgs.version_id, model_name=sgs.model.name, table_name=n)
