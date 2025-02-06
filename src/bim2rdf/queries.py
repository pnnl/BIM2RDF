from pathlib import Path
from typing import Self


def default_substitutions() -> dict:
    from bim2rdf_speckle.meta import prefixes as spkl_prefixes
    from bim2rdf_rules.rule import Rule
    return {
    'prefix.spkl':      spkl_prefixes.concept.uri,
    'prefix.spkl.meta': spkl_prefixes.meta.uri,
    'prefix.meta':      Rule.meta_prefix.uri,
    'model.arch.rooms&lights.name': 'architecture/rooms and lighting fixtures',
    }


class SPARQLQuery:
    class defaults:
        from bim2rdf_mapping.construct import default_dir as cdefault_dir
        dirs = [cdefault_dir]
        substitutions = default_substitutions()

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
          source: Iterable = defaults.dirs,
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


if __name__ == '__main__':
    from typing import Literal, List
    def sparql(*, idirs: List[Path]=SPARQLQuery.defaults.dirs,
          substitutions: Path|Literal['default']='default',
          odir=Path('substituted')):
        """substitute sparql queries"""
        idirs = [Path(d) for d in idirs]
        for d in idirs: assert(d.is_dir())
        if substitutions == 'default':
            substitutions = SPARQLQuery.defaults.substitutions
        else:
            substitutions = Path(substitutions)
            assert(substitutions.exists())
            from yaml import safe_load
            substitutions = safe_load(open(substitutions))
        odir = Path(odir)
        for d in idirs:
            for q in SPARQLQuery.s([d], substitutions=substitutions):
                assert(isinstance(q.source, Path))
                p: Path = odir / q.source.relative_to(d)
                p.parent.mkdir(parents=True, exist_ok=True)
                open(p, 'w').write(q.string)
        (odir / '.gitignore').touch()
        open(odir / '.gitignore', 'w').write('*')
        return odir

    from fire import Fire
    Fire({f.__name__:f for f in {sparql,}})
