
def default_substitutions() -> dict:
    from bim2rdf_speckle.meta import prefixes as                        spkl_prefixes
    from bim2rdf_rules.rule import                                      Rule
    from bim2rdf_rules.construct.rule import ConstructQuery as          CQ
    from bim2rdf_rules.topquadrant.rule import TopQuadrantInference as  TQI
    from bim2rdf_rules.ttl.rule import                                  ttlLoader
    _ = (
    (f'prefix.{Rule.meta_prefix.name}',         Rule.meta_prefix.uri,),
    (f'prefix.{ttlLoader.meta_prefix.name}',    ttlLoader.meta_prefix.uri),
    (f'prefix.{spkl_prefixes.concept.name}',    spkl_prefixes.concept.uri,),
    (f'prefix.{spkl_prefixes.meta.name}',       spkl_prefixes.meta.uri,),
    (f'prefix.{CQ.meta_prefix.name}',           CQ.meta_prefix.uri),
    (f'prefix.{TQI.meta_prefix.name}',          TQI.meta_prefix.uri),
    )
    def models():
        abbrs = {
            'arch': 'architecture',
            'elec': 'electrical',
            }
        _ = (
        ('arch.rooms&lights',   'rooms and lighting fixtures',),
        ('arch.lights',         'lighting devices',),
        ('arch.hvaczones',      'hvac zones',),
        ('elec.panels',         'panels'),
        ('elec.conn',           'electrical connections'),
        )
        _ = tuple(
            (f"model.{t[0]}.name",
             f"{abbrs[t[0].split('.')[0]]}/{t[1]}" )
             for t in _)
        from .engine import Run
        assert(set(_[1] for _ in _) == set(Run.defaults.model_names) )
        return _
    _ = _+models()
    assert(len(set(kv[0] for kv in _)) == len([kv[1] for kv in _]))
    _ = {kv[0]:kv[1] for kv in sorted(_, key=lambda t:t[0] )}
    return _

from pathlib import Path
from typing import Self
class SPARQLQuery:
    class defaults:
        from bim2rdf_mapping.construct import default_dir as cdefault_dir
        dirs = [cdefault_dir]
        substitutions = default_substitutions()

    def __init__(self, _s: str, *, substitutions=defaults.substitutions):
        self._s = _s
        self.substitutions = substitutions.copy()
    
    def check(self):
        from pyoxigraph import Store
        Store().query(self._s)
        return True
    
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
        self.check()
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
          odir=Path('substituted'),
          check=False,
          ):
        """evaluate templated sparql queries"""
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
                if check:
                    try: q.check()
                    except SyntaxError as se:
                        raise SyntaxError(str(se)+f' in {q.source}')
                assert(isinstance(q.source, Path))
                p: Path = odir / q.source.relative_to(d)
                p.parent.mkdir(parents=True, exist_ok=True)
                open(p, 'w').write(q.string)
        (odir / '.gitignore').touch()
        open(odir / '.gitignore', 'w').write('*')
        return odir

    from fire import Fire
    Fire({f.__name__:f for f in {sparql, default_substitutions}})
