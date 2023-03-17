

from .engine import Rules
def rules() -> Rules: #sparql mapping 'rules' for now 
    from .engine import ConstructQuery, Rules, rdflib_semantics, PyRule
    from . import mapping_dir
    from pathlib import Path
    _ = Path(mapping_dir).glob('**/*.sparql')
    _ = map(lambda p: open(p).read(),   _)
    _ = map(ConstructQuery,             _)
    _ = list(_) + [rdflib_semantics]
    _ = Rules([rdflib_semantics])
    return _



def db():
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.objects
    _ = query(_) # dict
    from speckle.objects import rdf
    _ = rdf(_) #
    fmt = 'text/turtle'
    #_ = parse(_, fmt) 
    from pyoxigraph import Store
    db = Store()
    db.bulk_load(_, fmt)
    from ontologies import get as get_ontology
    _ = get_ontology('brick')
    _ = open(_, 'rb')
    db.bulk_load(_, fmt)
    #from shacl_gen import shacl
    return db


from .engine import Engine
def fengine(*, rules=rules, db=db) -> Engine:
    from .engine import Engine, OxiGraph
    _ = Engine(
            rules(),
            OxiGraph(db()) )
    return _


if __name__ == '__main__':
    import fire
    
    from pathlib import Path
    def engine(*, out=Path('out.ttl')) -> Path:
        if not (str(out).lower().endswith('ttl')):
            raise ValueError('just use ttl fmt')
        _ = fengine()
        _()
        _ = _.db._store
        _.dump(str(out), 'text/turtle')
        return out

    fire.Fire(engine) # HAHH!!


