from engine.triples import Triples
from .engine import Rules, Callable, OxiGraph, Triples, PyRule


def rules(semantics = True) -> Rules: 
    from .engine import ConstructRule, Rules, rdflib_semantics
    from . import mapping_dir
    from pathlib import Path
    # mappings
    _ = Path(mapping_dir).glob('**/223p/*.rq') # https://www.iana.org/assignments/media-types/application/sparql-query
    _ = map(lambda p: open(p).read(),   _)
    _ = map(ConstructRule,             _)

    # geometry
    from .geometry import get_obj_assignment_rule
    _ = list(_)
    _ = _ + [PyRule(get_obj_assignment_rule('Lighting Fixtures', 'Rooms'))]

    # semantics
    _ = list(_) + ([PyRule(rdflib_semantics)] if semantics else [])

    #                     223p rules
    from .engine import pyshacl_rules 
    _ = _ + [PyRule(pyshacl_rules)] # ...but as one thing

    _ = Rules(_)
    return _


def get_ontology(ontology: str) -> Callable[[OxiGraph], Triples]:
    from .engine import get_data_getter
    from ontologies import get
    _ = get(ontology)
    _ = get_data_getter(_)
    return _


class SpeckleGetter(PyRule):

    def meta(self, data: Triples) -> Triples:
        # TODO
        _ = Triples()
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
    _ = _.decode()
    from .engine import get_data_getter
    _ = get_data_getter(_)
    return _


def get_speckle(stream_id, *, branch_id=None, object_id=None) -> Callable[[OxiGraph], Triples]:
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
    return _get_speckle(stream_id, object_id)
    
    
from validation.engine import Engine
def fengine(*, rules=rules) -> Engine:
    # functions for args
    from .engine import OxiGraph
    _ = Engine(
            rules(),
            OxiGraph(), MAX_ITER=20 )
    return _



from pathlib import Path
def engine(stream_id, *, branch_id=None, object_id=None,
           semantics=True,
           out=Path('out.ttl')) -> Path:
    # data/config for args
    if not (str(out).lower().endswith('ttl')):
        raise ValueError('just use ttl fmt')
    _ = fengine(rules=lambda: (
                    Rules([ PyRule(get_speckle(stream_id, branch_id=branch_id, object_id=object_id)) ,  ])
                    +rules(semantics=semantics)
                    ) )
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
    fire.Fire(engine) # HAHH!!


