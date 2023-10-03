from engine.triples import PyRuleCallable, Triples
from .engine import Rules, OxiGraph, Triples, PyRule
from typing import Callable


def rules(inference = True, mapping = True) -> Rules:
    _ = []
    from .engine import Rules
    if mapping:
        from .engine import ConstructRule
        from . import mapping_dir
        from pathlib import Path
        # mappings
        _ = Path(mapping_dir).glob('**/223p/*.rq') 
        _ = map(ConstructRule,              _)
        _ = list(_)

        # geometry calcs
        from .geometry import overlap
        _ = _ + [PyRule(overlap)]

    # inference
    if inference:
        _ = _ + [PyRule(get_ontology)]
        #                     223p rules
        from .engine import pyshacl_rules, rdflib_semantics
        _ = _ + [PyRule(rdflib_semantics), PyRule(pyshacl_rules)]

    _ = Rules(_)
    return _


def get_ontology(_: OxiGraph) -> Triples:
    from .util import get_data
    from ontologies import get
    _ = get('223p')
    _ = get_data(_)
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

    @staticmethod
    def get_branches(stream_id):
        assert(stream_id)
        from speckle.graphql import queries, query
        _ = queries()
        _ = _.general_meta()
        _ = query(_)
        _ = _['streams']['items']
        for d in _:
            if stream_id in {d['id'], d['name']}:
                stream_id = d['id']
                break
        if stream_id != d['id']: raise ValueError('stream not found')
        
        _ = d['branches']['items']
        _ = sorted(_, key=lambda i: i['createdAt'] )
        _ = tuple(d['id'] for d in _)
        return _

    @classmethod
    def multiple(cls, stream_id, branch_ids=[]):  # object_ids = []
        #  TODO 1:1 with object_id    (bid_n, oid_n) --> speckle export
        if not branch_ids: # analagous behavior to branch_id=None
            branch_ids = cls.get_branches(stream_id)
        for b in branch_ids:
            yield cls(stream_id, branch_id=b, )


    def meta(self, data: Triples) -> Triples:
        _ = self._getters.meta() 
        #_ = Triples()
        return _


# args will be stream, commit
def _get_speckle(stream_id, object_id) -> Callable[[OxiGraph], Triples]:
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.objects(stream_id, object_id)
    _ = query(_) # dict
    from speckle.objects import rdf as ordf
    _ = ordf(_) #
    _ = _.read()
    d = _.decode()
    from .util import get_data
    _ = lambda _: get_data(d)
    return _



def get_speckle_meta(stream_id, branch_id, object_id) -> Triples:
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.general_meta()
    _ = query(_)
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
            m[stream] = {id: s[id], name: s[name]}
            break
    
    for b in s[branches][items]:
        if branch_id == b[id]:
            m[branch] = {id: b[id], name: b[name], createdAt: b[createdAt] }
            break
    
    for c in b[commits][items]:
        if object_id == c[referencedObject]:
            m[commit] = {id: c[id], referencedObject: c[referencedObject], createdAt: c[createdAt] }
            break
    
    _ = m
    from speckle.meta import rdf as mrdf
    _ = mrdf(_) #
    from pyoxigraph import parse
    _ = parse(_, 'text/turtle')
    _ = Triples(_) # ! important! has blank nodes  but handled  centrally by '.deanon()' in PyRule.
    return _


#TODO: sparql query the full general_meta

def get_speckle(stream_id, *, branch_id=None, object_id=None):
    assert(stream_id)
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.general_meta()
    _ = query(_)
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
            objects=lambda _: Triples(),
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
    return N(
        objects=_get_speckle(stream_id, object_id),
        meta=lambda: get_speckle_meta(stream_id, branch_id, object_id)  )
    
    

def fengine(*, validation=True, rules=rules) -> 'Engine':
    # functions for args
    from .engine import OxiGraph
    if validation:
        from validation.engine import Engine
    else:
        from .engine import Engine
    _ = Engine(
            rules(),
            OxiGraph(), MAX_ITER=20)
    return _



from pathlib import Path
def engine(stream_id, *, branch_id=None, object_id=None,
           mapping = True,
           validation=True,
           inference=True,
           out=Path('out.ttl')) -> Path:
    # data/config for args
    if not (str(out).lower().endswith('ttl')):
        raise ValueError('just use ttl fmt')
    
    # parsing of branch_id is relegated to 
    if branch_id is None:
        # figuring this is the default mode of working from now.
        data_rules = Rules([sg for sg in SpeckleGetter.multiple(stream_id) ])
    elif isinstance(branch_id, (list, tuple)):
        data_rules = Rules([sg for sg in SpeckleGetter.multiple(stream_id, branch_id)])
    elif isinstance(branch_id, str):
        data_rules = Rules([SpeckleGetter(stream_id, branch_id=branch_id, object_id=object_id),])
    else:
        raise TypeError('branch id not processed')
    _ = fengine(
            rules=lambda: (
                    data_rules
                    +rules(
                        inference=inference,
                        mapping=mapping)
                    ),
            validation=validation,
        )
    _()
    _ = _.db._store
    _.dump(str(out), 'text/turtle')
    return out


if __name__ == '__main__':
    import fire
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    from engine.triples import logger
    logger.setLevel(logging.INFO)
    from .engine import logger
    logger.setLevel(logging.INFO)
    fire.Fire(engine) # HAHH!!


