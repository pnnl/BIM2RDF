

from .engine import Rules
def get_rules() -> Rules: #sparql mapping 'rules' for now 
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


def map_():
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.objects
    _ = query(_) # dict
    from speckle.objects import rdf
    _ = rdf(_)
    _  = _.encode() # bytes
    fmt = 'application/n-quads'
    #_ = parse(_, fmt) 
    from pyoxigraph import Store
    db = Store()
    db.bulk_load(_, fmt)
    r = get_rules()     # mapping
    from ontologies import get as get_ontology
    _ = get_ontology('brick')
    _ = open(_, 'rb')
    db.bulk_load(_, 'text/turtle')
    #from shacl_gen import shacl
    return db


def test():
    _ = map_()
    return _


if __name__ == '__main__':
    ...


