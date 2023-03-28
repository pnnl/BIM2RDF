from .engine import Rules, Callable, OxiGraph, Triples


def rules(semantics = True) -> Rules: #sparql mapping 'rules' for now 
    from .engine import ConstructQuery, Rules, rdflib_semantics
    from . import mapping_dir
    from pathlib import Path
    _ = Path(mapping_dir).glob('**/speckle/*.sparql')
    _ = map(lambda p: open(p).read(),   _)
    _ = map(ConstructQuery,             _)
    _ = list(_) + ([rdflib_semantics] if semantics else [])
    _ = [

        rdflib_semantics,
        ]
    _ = Rules(_)
    return _


def get_ontology(ontology: str) -> Callable[[OxiGraph], Triples]:
    from .engine import get_data_getter
    from ontologies import get
    _ = get(ontology)
    _ = get_data_getter(_)
    return _


# args will be stream, commit
def get_speckle(stream_id, object_id) -> Callable[[OxiGraph], Triples]: 
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.objects(stream_id, object_id)
    _ = query(_) # dict
    from speckle.objects import rdf
    _ = rdf(_) #
    _ = _.read()
    _ = _.decode()
    from .engine import get_data_getter
    _ = get_data_getter(_)
    return _



from .engine import Engine
def fengine(*, rules=rules) -> Engine:
    # functions for args
    from .engine import Engine, OxiGraph
    _ = Engine(
            rules(),
            OxiGraph(), MAX_ITER=10 )
    return _


from pathlib import Path
def engine(stream_id, *, object_id=None,
           semantics=True,
           out=Path('out.ttl')) -> Path:
    # data/config for args
    if not (str(out).lower().endswith('ttl')):
        raise ValueError('just use ttl fmt')
    _ = fengine(rules=lambda: rules(
                    semantics=semantics)
                    +Rules([get_speckle(stream_id, object_id)])
                    +Rules([get_ontology('223p')])
                    )
    _()
    _ = _.db._store
    _.dump(str(out), 'text/turtle')
    return out



if __name__ == '__main__':
    import fire
    fire.Fire(engine) # HAHH!!


