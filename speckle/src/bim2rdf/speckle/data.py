
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
        def parquets(self):
            from .rest import artifacts
            p = self.model.project  .id
            m = self.model          .id
            v = self                .id
            a = artifacts(project_id=p, model_id=m, version_id=v)
            _ = {}
            import pandas as pd
            from io import BytesIO as B
            for n,b in a.items():
                if n.endswith('.parquet'):
                    _[n] = pd.read_parquet(B(b))
            return _

    @cached_property
    def versions(self):
        return [self.Version(id=v['id'], model=self)
                for v in self.meta['versions']['items']]

from bim2rdf.cache import cache
@cache
def json2rdf(*p, **k):
    from json2rdf import j2r
    return j2r(*p, **k)


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
        for n, df in v.parquets.items():
            p = Path(n)
            df.to_parquet(p)
            ps.append(p)
        return ps
    Fire({f.__name__:f for f in (meta, data) })
