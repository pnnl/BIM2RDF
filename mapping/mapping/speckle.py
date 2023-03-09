

from .engine import Rules
def rules() -> Rules: #sparql mapping 'rules' for now 
    from .engine import ConstructQuery, Rules
    from . import mapping_dir
    from pathlib import Path
    _ = Path(mapping_dir).glob('**/*.sparql')
    _ = map(lambda p: open(p).read(),   _)
    _ = map(ConstructQuery,             _)
    _ = Rules(_)
    return _
# try:
#     from typing import Self
#     print('upgrade to python 3.11')
# except:
#     from typing_extensions import Self

# from .engine import Rules as _Rules
# class Rules(_Rules):
#     # def __new__(cls) -> Self:
#     #     return super().__new__()
#     @classmethod
#     def __call__(cls) -> '_Rules':
#         return get_rules()

# (query>json) > ttl > mapping/validation via shacl > ttl

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


def engine():
    from .engine import Engine, OxiGraph
    _ = Engine(
            rules(),
            OxiGraph(db()) )
    return _


def test():
    _ = engine()
    _ = _()
    return _


if __name__ == '__main__':
    ...


