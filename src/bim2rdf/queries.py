
class DefaultSubstitutions:
    from typing import List, Tuple
    @classmethod
    def models(cls) -> List[Tuple[str, str]]:
        abbrs = {
            'arch': 'architecture',
            'elec': 'electrical',
            }
        _ = [
        ('arch.rooms&lights',   'rooms and lighting fixtures',),
        ('arch.lights',         'lighting devices',),
        ('arch.hvaczones',      'hvac zones',),
        ('elec.panels',         'panels'),
        ('elec.conn',           'electrical connections'),
        ]
        _ = [
            (f"model.{t[0]}.name",
             f"{abbrs[t[0].split('.')[0]]}/{t[1]}" )
             for t in _]
        return _
    
    @classmethod
    def prefixes(cls) -> List[Tuple[str, str]]:
        from bim2rdf_speckle.meta import prefixes as                        spkl_prefixes
        from bim2rdf_rules.rule import                                      Rule
        from bim2rdf_rules.construct.rule import ConstructQuery as          CQ
        from bim2rdf_rules.topquadrant.rule import TopQuadrantInference as  TQI
        from bim2rdf_rules.topquadrant.rule import TopQuadrantValidation as TQV
        from bim2rdf_rules.ttl.rule import                                  ttlLoader
        _ = (
        (f'{Rule.meta_prefix.name}',        Rule.meta_prefix.uri,),
        (f'{ttlLoader.meta_prefix.name}',   ttlLoader.meta_prefix.uri),
        (f'{spkl_prefixes.concept.name}',   spkl_prefixes.concept.uri,),
        (f'{spkl_prefixes.meta.name}',      spkl_prefixes.meta.uri,),
        (f'{CQ.meta_prefix.name}',          CQ.meta_prefix.uri),
        (f'{TQI.meta_prefix.name}',         TQI.meta_prefix.uri),
        (f'{TQV.meta_prefix.name}',         TQV.meta_prefix.uri),
        ('rdfs',                            'http://www.w3.org/2000/01/rdf-schema#'),
        ('s223',                            'http://data.ashrae.org/standard223#'),
        ('qudt',                            'http://qudt.org/schema/qudt/'),
        ('qudt.unit',                       'http://qudt.org/vocab/unit/'),
        ('qudt.kind',                       'http://qudt.org/vocab/quantitykind/'),
        ('xsd',                             'http://www.w3.org/2001/XMLSchema#'),
        )
        from bim2rdf.rdf import Prefix as P
        objs = tuple(P(t[0], t[1]) for t in _)
        subs = tuple((f"prefix.{p.name}", p.uri) for p in objs)
        query = '\n'.join(f'PREFIX {p.name}: <{p.uri}>' for p in objs)+'\n\n'
        _ = subs + (('query.prefixes', query ),)
        return list(_)
    
    @staticmethod
    def check_unique(subs: List[Tuple[str, str]]) -> bool:
        # check uniqueness of keys should 'match' values.
        return len(set(kv[0] for kv in subs)) == len([kv[1] for kv in subs])
    
    @classmethod
    def mk(cls, subs: List[Tuple[str, str]],) -> dict:
        # before putting it into a dictionary
        assert(cls.check_unique(subs))
        _ = {kv[0]:kv[1] for kv in sorted(subs, key=lambda t:t[0] )}
        return _
    
    @classmethod
    def dict(cls, groups: set={'prefixes', 'models'}) -> dict:
        groups = set(groups)
        _ = []
        for g in groups: _ = _ + getattr(cls, g)()
        _ = cls.mk(_)
        return _

from pathlib import Path
from typing import Self
class SPARQLQuery:
    class defaults:
        from bim2rdf_mapping.construct import included_dir
        dirs = [included_dir]
        #                    more explicit as it's under sparqlqauery
        substitutions = DefaultSubstitutions.dict({'prefixes', 'models'})

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
    
    from functools import cached_property, cache
    @cache
    def check(self) -> bool:
        from pyoxigraph import Store
        _ = self.substitute()
        Store().query(_) # err
        return True
    @cache
    def substitute(self) -> str:
        _ = self._s
        from bim2rdf.utils.substitution import String
        _ = String(_, substitutions=self.substitutions)
        _ = _.substitute()
        return _
        #assert('construct' in _.lower())
    @cached_property
    def string(self):
        self.check() # err if syntax issue
        return self.substitute()
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
                open(p, 'w').write(q.substitute())
        (    odir / '.gitignore').touch()
        open(odir / '.gitignore', 'w').write('*')
        return odir
    
    from fire import Fire
    def default_substitutions(): return SPARQLQuery.defaults.substitutions
    Fire({f.__name__:f for f in {sparql, default_substitutions}})
