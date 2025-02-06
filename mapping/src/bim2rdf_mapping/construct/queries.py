from pathlib import Path
from typing import Self
class Query: # so generic
    class defaults:
        dir = Path(__file__).parent
        from bim2rdf_speckle.meta import prefixes as spkl_prefixes
        from bim2rdf_rules.rule import Rule
        substitutions = {
            'prefix.spkl':      spkl_prefixes.concept.uri,
            'prefix.spkl.meta': spkl_prefixes.meta.uri,
            'prefix.meta':      Rule.meta_prefix.uri,
            'model.arch.rooms&lights.name': 'architecture/rooms and lighting fixtures',
        }

    def __init__(self, _s: str, *, substitutions=defaults.substitutions):
        self._s = _s
        self.substitutions = substitutions.copy()
    
    @classmethod
    def from_path(cls, p: Path, *, substitutions=defaults.substitutions) -> Self:
        p = Path(p)
        assert(p.exists())
        _ = cls(p.read_text(), substitutions=substitutions)
        _.source = p
        return _

    from functools import cached_property
    @cached_property
    def string(self):
        _ = self._s
        from bim2rdf.utils.substitution import String
        _ = String(_)
        _ = _.substitue(self.substitutions)
        #assert('construct' in _.lower())
        return _
    def __str__(self): return self.string

    from typing import Iterable
    @classmethod
    def s(cls,
          source: Iterable = [defaults.dir],
          *, substitutions=defaults.substitutions) -> Iterable[Self]:
        for src in source:
            if isinstance(src, str):
                if Path(src).exists():
                    src = Path(src)
                    yield from cls.s([src], substitutions=substitutions)
                else:
                    yield cls(src, substitutions=substitutions)
            else:
                assert(isinstance(src, Path))
                if src.is_dir():
                    yield from cls.s(src.glob('**/*.rq'), substitutions=substitutions)
                else:
                    assert(src.is_file())
                    yield cls.from_path(src, substitutions=substitutions)
    
default = tuple(Query.s())

if __name__ == '__main__':
    from typing import Literal
    def _(*, i=Path(Query.defaults.dir),
          substitutions: Path|Literal['default']='default',
          o=Path('construct')):
        i = Path(i)
        if substitutions == 'default':
            substitutions = Query.defaults.substitutions
        else:
            substitutions = Path(substitutions)
            assert(substitutions.exists())
            from yaml import safe_load
            substitutions = safe_load(open(substitutions))
        o = Path(o)
        for q in Query.s([i], substitutions=substitutions):
            assert(isinstance(q.source, Path))
            p = q.source.relative_to(i)
            p: Path = o / p
            p.parent.mkdir(parents=True, exist_ok=True)
            open(p, 'w').write(q.string)
        return o

    from fire import Fire
    Fire(_)
