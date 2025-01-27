from ..rules import Rule, Store, Prefix
class ConstructQuery(Rule):
    meta_prefix =    Prefix('meta',    'urn:meta:bim2rdf:ConstructQuery:')
    def __init__(self, query: str, *, name=None):
        assert('construct' in query.lower())
        self.query = query
        self.name = name
    from pathlib import Path
    @classmethod
    def from_path(cls, p: Path):
        _ = cls(open(p).read(), name=p.name)  #idk if name will be unique enough
        _.path = p
        return _
    
    from functools import cached_property
    @cached_property
    def spec(self):
        _ = {'name': self.name, }
        #if hasattr(self, 'path'): need?
        #    _['path'] = str(self.path)
        return _

    def data(self, db: Store):
        _ =  db.query(str(self.query),)
        from pyoxigraph import QueryTriples
        assert(isinstance(_, QueryTriples))
        yield from _
# need to create MappingConstructQuery(source, target)?