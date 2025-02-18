from ..rule import Rule
class ConstructQuery(Rule):
    from ..rule import Prefix
    meta_prefix =    Prefix('construct.meta',    'urn:meta:bim2rdf:ConstructQuery:')
    def __init__(self, query: str, *, name=None):
        assert('construct' in query.lower())
        self.query = query
        self.name = name
    
    from pathlib import Path
    @classmethod
    def mk_name(cls, src: Path) -> str:
        assert(isinstance(src, cls.Path))
        _ = src.name
        return _

    @classmethod
    def from_path(cls, p: Path):
        p = cls.Path(p)
        _ = cls(open(p).read(), name=cls.mk_name(p) )  #idk if name will be unique enough
        _.path = p
        return _
    
    from functools import cached_property
    @cached_property
    def spec(self):
        _ = {'name': self.name, }
        #if hasattr(self, 'path'): need?
        #    _['path'] = str(self.path)
        return _

    from ..rule import Store
    def data(self, db: Store):
        _ =  db.query(str(self.query),)
        from pyoxigraph import QueryTriples
        assert(isinstance(_, QueryTriples))
        yield from _
# need to create MappingConstructQuery(source, target)?