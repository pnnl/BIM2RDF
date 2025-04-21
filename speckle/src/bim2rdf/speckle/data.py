
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
        def rootid(self) -> str:
            return self.meta['referencedObject']

        class Json:
            def __init__(self, version: 'Version'):
                self.version = version
            def data(self) -> dict:
                from .graphql import queries, query
                _ = queries.objects(project_id=self.version.model.project.id, object_id=self.version.rootid)
                _ = query(_) # dict
                return _

            def wo_geometry(self):
                _ = self.data()
                from boltons.iterutils import remap#, get_path
                def notvec(p,k,v):
                    if p:
                        if k in {'matrix', 'data', 'faces', 'vertices'}:
                            if isinstance(v, list):
                                if all(isinstance(e, (int, float)) for e in v):
                                    return False
                    return True
                def notgeo(p,k,v):
                    # should have the above vec keys
                    types = {'Objects.Other.Transform', "Speckle.Core.Models.DataChunk"}
                    id = 'id'
                    st = 'speckle_type'
                    if isinstance(v, dict):
                        if (st in v) and (id in v):
                            if (v[st] in types) or (v[st].lower().startswith('objects.geometry') ):
                                return False
                    return True
                _ = remap(_, notgeo)
                return _
        def json(self):
            return self.Json(self)
        
        from typing import Callable
        def ttl(self, *, json_method:str|Callable=Json.wo_geometry, **kw):
            from .meta import prefixes
            dp = prefixes.data(project_id=self.model.project.id, object_id="") # objid filled in
            _ = self.json()
            _ = getattr(_, json_method.__name__ if not isinstance(json_method, str) else json_method) # ?
            _ = _()
            _ = json2rdf(_,
                    subject_id_keys=('id',),     object_id_keys=('referencedId', 'connectedConnectorIds'),
                    id_prefix=(str(dp.name), str(dp.uri)),
                    key_prefix=(str(prefixes.concept.name), str(prefixes.concept.uri)),
                    **kw)
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
    def ttl(project_id, version_id, geometry: bool=False):
        return version(project_id, version_id).ttl(json_method='data' if geometry else 'wo_geometry')
    def json(project_id, version_id):
        _ = version(project_id, version_id)
        _ = _.json().data()
        from json import dumps
        _ = dumps(_, indent=2)
        return _
    Fire({f.__name__:f for f in (meta, json, ttl) })
