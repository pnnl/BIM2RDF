from engine.triples import Engine, PyRuleCallable, Triples
from .engine import ConstructRule, Rules, OxiGraph, Triples, PyRule
from typing import Callable, Iterable
from pathlib import Path


from . import mapping_dir
maps_dir = mapping_dir / 'rules'
def rules_from_dir(maps_dir=maps_dir):
    from .engine import ConstructRule
    # mappings
    _ = Path(maps_dir).glob('**/*.rq')
    _ = map(ConstructRule,              _)
    _ = list(_)
    return _


def mk_rules(*,
          paths: Path | Iterable[Path] | None = maps_dir,
          inference = True, 
            ) -> Rules:
    _ = []
    from .engine import Rules
    if paths:
        if isinstance(paths, Path):
            return mk_rules(paths=[paths], inference=inference)
        else:
            for p in paths:
                assert(p.exists())
                if p.is_dir():
                    _ = _ + rules_from_dir(p)
                else:
                    assert(p.suffix == '.rq')
                    _ = _ + [ ConstructRule(p) ]

    # inference
    if inference:
        #                     223p rules
        from .engine import topquadrant_rules
        #from .engine import rdflib_rdfs
        _ = _ + [
            #PyRule(rdflib_rdfs),
            PyRule(topquadrant_rules),
                ]

    _ = Rules(_)
    return _


def query(q):
    from speckle.graphql import query, client
    _ = query(q, lambda: client()) # need this to be 'live'
    return _


class SpeckleGetter(PyRule):

    def __init__(self, project_id, model_id=None, object_id=None) -> None:
        self.project_id = project_id
        self.model_id = model_id
        self.object_id = object_id
        _ = get_speckle(project_id, model_id=model_id, object_id=object_id)
        super().__init__(_.objects)
        self._getters = _

    def __repr__(self) -> str:
        _ = f"{self.__class__.__name__}"
        _ = _ + f"(project_id={self.project_id},"
        _ = _ + f"model_id={self.model_id},"
        _ = _ + f"object_id={self.object_id})"
        return _
    
    def get_models(project_id)-> 'model names':
        assert(project_id)
        _ = query_speckle_meta()
        _ = _['projects']['items']
        for d in _:
            if project_id in {d['id'], d['name']}:
                project_id = d['id']
                break
        if project_id != d['id']: raise ValueError('project not found')
        
        _ = d['models']['items']
        _ = sorted(_, key=lambda i: i['createdAt'] )
        _ = tuple(d['name'] for d in _)
        return _
    
    @staticmethod
    def get_projects() -> 'projects':
        _ = query_speckle_meta()
        from types import SimpleNamespace as NS
        return tuple(
            NS(id=i['id'], name=i['name'])
            for i in  _['projects']['items'])

    @classmethod
    def multiple(cls, project_id, model_ids=[]):  # object_ids = []
        #  TODO 1:1 with object_id    (bid_n, oid_n) --> speckle export
        if not model_ids: # analagous behavior to model_id=None
            model_ids = cls.get_models(project_id)
        for b in model_ids:
            yield cls(project_id, model_id=b, )

    def meta(self, ) -> Triples:
        _ = self._getters.meta()
        return _
    
def namespaces():
    _ = SpeckleGetter.get_projects()
    from speckle import object_uri
    from ontologies import namespace
    from rdflib import URIRef
    _ = (s for s in _  if s.name.startswith('bldg'))
    _ = map(lambda i: namespace(f"{i.name}", URIRef(object_uri(i.id,)) ), _)
    _ = tuple(_)
    return _



# from datetime import timedelta, datetime
# def my_ttu(_key, value, now):
#     # assume value.ttl contains the item's time-to-live in hours
#     return now + timedelta(hours=value.ttl)
# @get_cache('specklemeta', type='TLRUCache', maxsize=1, ttu=my_ttu, timer=datetime.now ) #
from .cache import get_cache, get_dir
@get_cache('specklemeta', dir=get_dir() / 'data',  maxsize=1)
def query_speckle_meta():
    from speckle.graphql import queries
    _ = queries()
    _ = _.general_meta()
    _ = query(_)
    _ = _['activeUser']
    return _

# TODO: sparql query the full general_meta instead of writing python
from functools import lru_cache
@lru_cache
def get_speckle_meta_json(project_id, model_id, object_id) -> dict:
    _ = query_speckle_meta()
    id = 'id'
    name = 'name'
    items = 'items'
    project = 'project'; projects = 'projects'
    model = 'model'; models = 'models'
    createdAt = 'createdAt'
    referencedObject = 'referencedObject'
    version = 'version'; versions = 'versions'
    m = {}
    
    for s in _[projects][items]:
        if project_id == s[id]:
            #m[project] = {id: s[id], name: s[name]}
            break
    # just keep model Name. it's the only one that's used
    for b in s[models][items]:
        if model_id == b[id]:
            m[model] = {id: b[id], name: b[name],} # createdAt: b[createdAt] }
            break
    
    for c in b[versions][items]:
        if object_id == c[referencedObject]:
            #m[version] = {id: c[id], referencedObject: c[referencedObject], createdAt: c[createdAt] }
            break
    
    _ = m
    return _


def get_speckle(project_id, *, model_id=None, object_id=None):
    assert(project_id)
    _ = query_speckle_meta()
    _ = _['projects']['items']
    for d in _:
        if project_id in {d['id'], d['name']}:
            project_id = d['id']
            break
    if project_id != d['id']: raise ValueError('project not found')
    
    _ = d['models']['items']
    _ = sorted(_, key=lambda i: i['createdAt'] )
    for d in _:
        if model_id in {d['id'], d['name']}:
            model_id = d['id']
            break
    if model_id:
        if model_id != d['id']:
            raise ValueError('model not found')
    else:
        model_id = d['id']
    
    _ = d['versions']['items']
    from types import SimpleNamespace as N
    if not len(_):  # if there are no items
        return N(
            objects=lambda db: Triples(),
            meta=lambda: Triples(),
        )

    _ = sorted(_, key=lambda i: i['createdAt'] )
    for d in _:
        if d['referencedObject'] == object_id:
            object_id = d['referencedObject']
            break
    if object_id:
        if object_id != d['referencedObject']:
            raise ValueError('object not found')
    else:
        object_id = d['referencedObject']

    _ = d
    assert(project_id)
    assert(object_id)

    def sideload(db: OxiGraph):
        # TODO: just the meta model name is enough
        m = get_speckle_meta_json(project_id, model_id, object_id)
        from .cache import get_cache as cache, get_dir
        # project_id is not a name here so caching is fine.
        from speckle.data import get_json
        get_json = cache('speckle', dir=get_dir() / 'data', maxsize=100)(get_json)
        d = get_json(project_id, object_id)
        @cache('speckle_rdf', dir=get_dir() / 'func',  maxsize=100)
        def to_rdf(project_id, object_id): # object_id just used for cache lookup
            # args are just used for the cache
            # to identify the result
            from speckle.json2rdf import to_rdf
            _ = to_rdf(d, m, project_id=project_id)
            return _
        _ = to_rdf(project_id, object_id)
        _ = _ + '\n'  # idk fixes issue to make rdfformat.turtle!!
        from io import StringIO
        _ = StringIO(_)
        from pyoxigraph import RdfFormat
        db._store.bulk_load(_, RdfFormat.TURTLE)
        return Triples()
    return N(
        objects=sideload,
        meta=lambda: Triples()  )  
        

def fengine(og=OxiGraph(), *,
        rules=mk_rules(),
        validation=True,
        deanon=True,
        max_cycles=20) -> 'Engine':
    if validation:
        from validation.engine import Engine
    else:
        from .engine import Engine
    _ = Engine(
            rules,
            og,
            deanon=deanon,
            MAX_ITER=max_cycles
            )
    return _


allowed_models = {
    'architecture', 'electrical', 'mechanical', 'plumbing',
}

from pathlib import Path
from typing import Iterable
from pyoxigraph import Store
def map_(project_id, *, model_ids=None,
        rules: Path | Iterable[Path] | None = maps_dir,
        max_cycles=10,
        inference=False,
        validation=False,
        init=OxiGraph()
        ) -> Store:
    object_id=None
    assert(
        (project_id in (s.id for s in SpeckleGetter.get_projects()) )
        or
        (project_id in (s.name for s in SpeckleGetter.get_projects()) )
          )

    # parsing of model_id is relegated to
    if model_ids is None:
        # figuring this is the default mode of working from now.
        data_rules = Rules([sg for sg in SpeckleGetter.multiple(project_id) if sg.model_id.split('/')[0].lower() in allowed_models ])
    elif isinstance(model_ids, (list, tuple, set)):
        data_rules = Rules([sg for sg in SpeckleGetter.multiple(project_id, model_ids)])
    elif isinstance(model_ids, str):
        data_rules = Rules([SpeckleGetter(project_id, model_id=model_ids, object_id=object_id),])
    else:
        raise TypeError('model id not processed')
    
    if rules:
        if isinstance(rules, (list, tuple, set)):
            rules = tuple(Path(_) for _ in rules)
        else:
            rules = (Path(rules),)
    
    # throw and forget mode. not optimized but don't have to manage.
    # _ = fengine(
    #         rules=(data_rules
    #                 +rules(
    #                     inference=inference,
    #                     rules_dir=rules_dir)),
    #         validation=validation,
    #         max_cycles=max_cycles,
    #     )
    # _()
    # some manual rules handling to optimize processing time
    # 1. load data / "one-time rules"
    from .engine import get_ontology
    _ = fengine(
            og=init,
            rules=data_rules+(Rules([PyRule(get_ontology)]) if rules else Rules([]) ),
            validation=False,
            deanon=False,
            max_cycles=1)() # no need to keep spinning
    if rules:
    # 2. "mappings"
        _ = fengine(og=_.db,
            rules=mk_rules(
                paths=rules,
                inference=False),
            validation=False,
            deanon=True,
            max_cycles=max_cycles)()
    # 3. inferencing 
    if inference:
        _ = fengine(og=_.db,
            rules=mk_rules(
                paths=None,
                inference=inference),
            validation=False,
            deanon=True,
            max_cycles=max_cycles)()
    # 4. validation
    if validation:
        _ = fengine(og=_.db,
            rules=mk_rules(
                paths=None,
                inference=False),
            validation=validation,
            deanon=False, # doest matter.
            max_cycles=max_cycles)()
    
    return _.db._store


def write_map(project_id, *, model_ids=None,
            rules: Path | Iterable[Path] | None = maps_dir,
            max_cycles=10,
            inference=False,
            validation=False,
            out=Path('db')
            ) -> Path:
    out = Path(out)
    if out.exists():
        if not out.is_dir():
            raise IOError(f'{out} is not dir')
        if tuple(out.iterdir()):
            raise IOError(f'{out} not empty')
    init = OxiGraph(Store(out))
    _ = map_(project_id, model_ids=model_ids,
            rules = rules,
            max_cycles=max_cycles,
            inference=inference,
            validation=validation,
            init=init)
    return out


if __name__ == '__main__':
    import fire
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    from engine.triples import logger
    logger.setLevel(logging.INFO)
    from .engine import logger
    logger.setLevel(logging.INFO)
    from validation.engine import logger
    logger.setLevel(logging.INFO)
    
    fire.Fire(write_map)
    
