
class Project:
    """convenience wrapper around graphql"""
    def __init__(self, id: str):
        _ = self._s()
        for p in _:
            if id == p['id']: break
        if p['id'] != id:
            raise ValueError('project not found')
        self.id = id
    
    @classmethod
    def from_name(cls, name: str):
        _ = [p for p in cls.s() if p.name == name ]
        assert(len(_) == 1)
        return _[0]

    from functools import cached_property, cache
    @cached_property
    def name(self):
        return self.meta['name']
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"

    @classmethod
    @cache
    def _s(cls, *, filter=lambda p: True):
        from bim2rdf.speckle.graphql import queries, query
        _ = queries.general_meta()
        _ = query(_)
        _ = _['activeUser']['projects']['items']
        _ = [p for p in _ if filter(p)]
        return _
    @classmethod
    def s(cls, *p, **kw):
        return [cls(_['id']) for _ in cls._s(*p, **kw)]
    @cached_property
    def meta(self) -> dict:
        for p in self._s():
            if p['id'] == self.id:
                return p

    @cached_property
    def models(self):
        _ =  self.meta['models']['items']
        _ = [Model(project=self, id=m['id'], ) for m in _]
        return _


class Model:
    """convenience wrapper around graphql"""
    def __init__(self, *, project: Project, id: str):
        self.project = project
        self.id = id

    from functools import cached_property
    @cached_property
    def meta(self) -> dict:
        for m in self.project.meta['models']['items']:
            if m['id'] == self.id:
                return m
        # shouldn't come here
        assert(not True)

    @cached_property
    def name(self):
        return self.meta['name']

    def __repr__(self):
        return f"{self.__class__.__name__}(project={repr(self.project)}, id={self.id}, name={self.name})"
    
    class Version:
        """convenience wrapper around graphql"""
        def __init__(self, *, id, model):
            self.id = id
            self.model: Model = model
        def __repr__(self):
            return f"{self.__class__.__name__}(model={repr(self.model)}, id={self.id})"
        
        from functools import cached_property
        @cached_property
        def meta(self):
            for v in self.model.meta['versions']['items']:
                if v['id'] == self.id:
                    return v
            assert(not True)

        @cached_property
        def artifacts_list(self):
            from .rest import artifacts_list
            p = self.model.project  .id
            m = self.model          .id
            v = self                .id
            al = artifacts_list(project_id=p, model_id=m, version_id=v)
            return al

        def table(self, name: str):
            assert(name.endswith('.parquet'))
            p = self.model.project  .id
            m = self.model          .id
            v = self                .id
            from .rest import artifact
            _ = artifact(project_id=p, model_id=m, version_id=v, name=name)
            import pandas as pd
            from io import BytesIO as B
            _ = pd.read_parquet( B(_))
            return _

        def parquet_list(self):
            for i in self.artifacts_list['files']:
                if 'name' and 'url' in i:
                    n = i['name']
                    if n.endswith('.parquet'):
                        yield n

    @cached_property
    def versions(self):
        return [self.Version(id=v['id'], model=self)
                for v in self.meta['versions']['items']]



if __name__ == '__main__':
    from fire import Fire
    def meta(project_id: str):
        return Project(project_id).meta
    def version(project_id, version_id):
        for m in Project(project_id).models:
            for v in m.versions:
                if v.id == version_id:
                    return v
    def data(project_id, version_id, geometry: bool=False):
        p = Project(project_id)
        v = version(project_id, version_id)
        ps = []
        from pathlib import Path
        for p in v.parquet_list():
            df = v.table(p)
            p = Path(p)
            df.to_parquet(p)
        return ps
    Fire({f.__name__:f for f in (meta, data) })
