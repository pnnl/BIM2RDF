from sys import maxsize
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

    def __init__(self, stream_id, branch_id=None, object_id=None) -> None:
        self.stream_id = stream_id
        self.branch_id = branch_id
        self.object_id = object_id
        _ = get_speckle(stream_id, branch_id=branch_id, object_id=object_id)
        super().__init__(_.objects)
        self._getters = _

    def __repr__(self) -> str:
        _ = f"{self.__class__.__name__}"
        _ = _ + f"(stream_id={self.stream_id},"
        _ = _ + f"branch_id={self.branch_id},"
        _ = _ + f"object_id={self.object_id})"
        return _
    
    def get_branches(stream_id)-> 'branch names':
        assert(stream_id)
        _ = query_speckle_meta()
        _ = _['streams']['items']
        for d in _:
            if stream_id in {d['id'], d['name']}:
                stream_id = d['id']
                break
        if stream_id != d['id']: raise ValueError('stream not found')
        
        _ = d['branches']['items']
        _ = sorted(_, key=lambda i: i['createdAt'] )
        _ = tuple(d['name'] for d in _)
        return _
    
    @staticmethod
    def get_streams() -> 'streams':
        _ = query_speckle_meta()
        from types import SimpleNamespace as NS
        return tuple(
            NS(id=i['id'], name=i['name'])
            for i in  _['streams']['items'])

    @classmethod
    def multiple(cls, stream_id, branch_ids=[]):  # object_ids = []
        #  TODO 1:1 with object_id    (bid_n, oid_n) --> speckle export
        if not branch_ids: # analagous behavior to branch_id=None
            branch_ids = cls.get_branches(stream_id)
        for b in branch_ids:
            yield cls(stream_id, branch_id=b, )

    def meta(self, ) -> Triples:
        _ = self._getters.meta()
        return _
    
def namespaces():
    _ = SpeckleGetter.get_streams()
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
from .cache import get_cache
@get_cache('specklemeta', maxsize=1)
def query_speckle_meta():
    from speckle.graphql import queries
    _ = queries()
    _ = _.general_meta()
    _ = query(_)
    return _

# TODO: sparql query the full general_meta instead of writing python
from functools import lru_cache
@lru_cache
def get_speckle_meta_json(stream_id, branch_id, object_id) -> dict:
    _ = query_speckle_meta()
    id = 'id'
    name = 'name'
    items = 'items'
    stream = 'stream'; streams = 'streams'
    branch = 'branch'; branches = 'branches'
    createdAt = 'createdAt'
    referencedObject = 'referencedObject'
    commit = 'commit'; commits = 'commits'
    m = {}
    
    for s in _[streams][items]:
        if stream_id == s[id]:
            #m[stream] = {id: s[id], name: s[name]}
            break
    # just keep branch Name. it's the only one that's used
    for b in s[branches][items]:
        if branch_id == b[id]:
            m[branch] = {id: b[id], name: b[name],} # createdAt: b[createdAt] }
            break
    
    for c in b[commits][items]:
        if object_id == c[referencedObject]:
            #m[commit] = {id: c[id], referencedObject: c[referencedObject], createdAt: c[createdAt] }
            break
    
    _ = m
    return _


def get_speckle(stream_id, *, branch_id=None, object_id=None):
    assert(stream_id)
    _ = query_speckle_meta()
    _ = _['streams']['items']
    for d in _:
        if stream_id in {d['id'], d['name']}:
            stream_id = d['id']
            break
    if stream_id != d['id']: raise ValueError('stream not found')
    
    _ = d['branches']['items']
    _ = sorted(_, key=lambda i: i['createdAt'] )
    for d in _:
        if branch_id in {d['id'], d['name']}:
            branch_id = d['id']
            break
    if branch_id:
        if branch_id != d['id']:
            raise ValueError('branch not found')
    else:
        branch_id = d['id']
    
    _ = d['commits']['items']
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
    assert(stream_id)
    assert(object_id)

    def sideload(db: OxiGraph):
        # TODO: just the meta branch name is enough
        m = get_speckle_meta_json(stream_id, branch_id, object_id)
        from .cache import get_cache as cache
        # stream_id is not a name here so caching is fine.
        from speckle.data import get_json
        get_json = cache('speckle', maxsize=100)(get_json)
        d = get_json(stream_id, object_id)
        @cache('speckle_rdf', maxsize=100)
        def to_rdf(stream_id, object_id):
            # args are just used for the cache
            # to identify the result
            from speckle.json2rdf import to_rdf
            _ = to_rdf(d, meta=m)
            return _
        _ = to_rdf(stream_id, object_id)
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


allowed_branches = {
    'architecture', 'electrical', 'mechanical', 'plumbing',
}

from pathlib import Path
from typing import Iterable
from pyoxigraph import Store
def map_(stream_id, *, branch_ids=None,
        rules: Path | Iterable[Path] | None = maps_dir,
        max_cycles=10,
        inference=False,
        validation=False,
        init=OxiGraph()
        ) -> Store:
    object_id=None
    assert(
        (stream_id in (s.id for s in SpeckleGetter.get_streams()) )
        or
        (stream_id in (s.name for s in SpeckleGetter.get_streams()) )
          )

    # parsing of branch_id is relegated to
    if branch_ids is None:
        # figuring this is the default mode of working from now.
        data_rules = Rules([sg for sg in SpeckleGetter.multiple(stream_id) if sg.branch_id.split('/')[0].lower() in allowed_branches ])
    elif isinstance(branch_ids, (list, tuple, set)):
        data_rules = Rules([sg for sg in SpeckleGetter.multiple(stream_id, branch_ids)])
    elif isinstance(branch_ids, str):
        data_rules = Rules([SpeckleGetter(stream_id, branch_id=branch_ids, object_id=object_id),])
    else:
        raise TypeError('branch id not processed')
    
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


def write_map(stream_id, *, branch_ids=None,
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
    _ = map_(stream_id, branch_ids=branch_ids,
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
    
