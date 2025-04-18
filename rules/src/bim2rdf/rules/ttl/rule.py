from ..rule import Rule
class URI(str): ...

class ttlLoader(Rule):
    from bim2rdf.core.rdf import Prefix# , URI
    meta_prefix = Prefix('ttl.meta', "urn:meta:bim2rdf:ttlLoader:")

    from pathlib import Path
    def __init__(self, source: URI | Path| str):
        self.source = source
    
    from functools import cached_property
    @cached_property
    def spec(self): return {'source': str(self.source) }
    
    @classmethod
    def parse_src(cls, source):
        from pyoxigraph import parse, RdfFormat
        if isinstance(source, cls.Path):
            return parse(open(source), format=RdfFormat.TURTLE)
        else:
            assert(isinstance(source, (str, URI)))
            if isinstance(source, str):
                if cls.Path(source).exists():
                    return cls.parse_src(cls.Path(source))
            from urllib.request import urlopen
            _ = urlopen(source)
            _ = _.read()
            _ = parse(_, format=RdfFormat.TURTLE)
            return _

    def data(self, _):
        _ = self.parse_src(self.source)
        _ = (q.triple for q in _)
        yield from _
