
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
        from bim2rdf.speckle.meta import prefixes as                        spkl_prefixes
        from bim2rdf.rules.rule import                                      Rule
        from bim2rdf.rules.construct.rule import ConstructQuery as          CQ
        from bim2rdf.rules.topquadrant.rule import TopQuadrantInference as  TQI
        from bim2rdf.rules.topquadrant.rule import TopQuadrantValidation as TQV
        from bim2rdf.rules.ttl.rule import                                  ttlLoader
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
        from bim2rdf.core.rdf import Prefix as P
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
        from bim2rdf.mapping.construct import included_dir
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
        from bim2rdf.core.utils.substitution import String
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


class Queries:
    def __init__(self):
        self._set_included_mappings()
    
    def _set_included_mappings(self):
        for q in SPARQLQuery.s():
            n  = q.source
            assert(isinstance(n, Path))
            n = n.stem#.replace('-', '_').replace(' ', '_')
            setattr(self, n, q.string)

    @property
    def mapped(self) -> str:
        _ ="""
        prefix c: <${prefix.construct.meta}>
        construct {?s ?p ?o.}
        WHERE {
        <<?s ?p ?o>> c:name ?mo.
        filter (CONTAINS(?mo, ".mapping.") || CONTAINS(?mo, ".data.") ) 
        }"""
        return self.mk(_)
    @property
    def mapped_and_inferred(self) -> str:
        _ ="""
        prefix c: <${prefix.construct.meta}>
        prefix i: <${prefix.tq.inf.meta}>
        construct {?s ?p ?o.}
        WHERE {
            {<<?s ?p ?o>> c:name ?mo.
            filter (CONTAINS(?mo, ".mapping.") || CONTAINS(?mo, ".data."))}
        union
            {<<?s ?p ?o>> i:data ?_. } # there's also i:shapes
        }"""
        return self.mk(_)
    @property
    def ontology(self) -> str:
        _ = """
        prefix t: <${prefix.ttl.meta}>
        construct {?s ?p ?o.}
        WHERE {
        <<?s ?p ?o>> t:source ?mo.
        filter (CONTAINS(?mo, "ontology.ttl") )
        }"""
        return self.mk(_)
    
    @property
    def validation(self) -> str:
        _ = """
        prefix v: <${prefix.tq.val.meta}>
        construct {?s ?p ?o.}
        where {<<?s ?p ?o>> v:data ?_.}
        """
        return self.mk(_)
    #     @property just for ref. does not gen triples
    # def shacl_report(self):
    #     from .query import Prefixes, Node, known_prefixes
    #     S = lambda n: Node('sh', n)
    #     vr = S('ValidationResult')
    #     fn = S('focusNode')
    #     rm = S('resultMessage')
    #     vl = S('value')
    #     rp = S('resultPath')
    #     ss = S('sourceShape')  
    #     sv = S('resultSeverity')
    #     sc = S('sourceConstraintComponent')
    #     _ = Prefixes(p for p in known_prefixes if 'shacl' in str(p.uri) )
    #     _ = str(_)
    #     _ = _ + f"""
    #     select  {fn.var} {rm.var} {vl.var} {rp.var} {sv.var} {ss.var} where {{
    #     {vr.var} a {vr}.
    #     optional {{{vr.var} {fn} {fn.var}}}.
    #     optional {{{vr.var} {rm} {rm.var}}}.
    #     optional {{{vr.var} {vl} {vl.var}}}.
    #     optional {{{vr.var} {rp} {rp.var}}}.
    #     optional {{{vr.var} {sv} {sv.var}}}.
    #     optional {{{vr.var} {ss} {ss.var}}}.
    #     }}
    #     """
    #     return _

    @property
    def _test(self):
        return self.mk("""
        ${query.prefixes}
        construct {?s ?p ?o} where {?s ?p ?o}
        """)
    
    @property
    def names(self):
        _ = (a for a in dir(self)
            if (not a.startswith('_')) and (a not in {'mk', 'names'}))
        _ = frozenset(_)
        return _
    
    @classmethod
    def mk(cls, q: str, subs=True):
        if subs:
            return str(SPARQLQuery(q))
        else:
            return q
_ = Queries()
queries = {n:getattr(_, n) for n in _.names} ; del _

from pyoxigraph import Store
def query(*, db: Path|Store|str=Path('db'), query: str|Path,
          run_params: dict|Path=Path('params.yaml'),
          out:Path|str|None=Path('result.ttl'),):
    # mostly meant to be used from the cli
    """
    evaluate construct query mainly to extract subgraphs of the bim2rdf process
    'query' will either be the /name/ of the query or can be a path to a query
    params is used just to make a spkl.data prefix
    """
    if Path(query).exists():
        query = Path(query).read_text()
    else:
        assert(isinstance(query, str))
        query = queries[query]
    assert('construct' in query.lower() )
    query = str(SPARQLQuery(query))
    if isinstance(db, (Path,str)):
        db = Path(db)
        assert(db.exists())
        assert(db.is_dir())
        db = Store(db)
    else:
        assert(isinstance(db, Store))
    from pyoxigraph import serialize, RdfFormat
    r = db.query(query)
    r = serialize(r, format=RdfFormat.TURTLE)
    from rdflib import Graph
    r = Graph().parse(data=r, format='ttl')
    prefixes = {'.'.join(n.split('.')[1:]):s
                for n,s in SPARQLQuery.defaults.substitutions.items()
                if n.startswith('prefix.') }
    if Path(run_params).exists():
        run_params = Path(run_params)
        from yaml import safe_load
        run_params = safe_load(open(run_params).read())
    assert(isinstance(run_params, dict))
    if 'project_name' in run_params:
        from bim2rdf.speckle.data import Project
        _ = Project.from_name(run_params['project_name'])
        project_id = _.id
    else:
        project_id = run_params['project_id']
    from bim2rdf.speckle.meta import prefixes as sp
    _ = sp.data(project_id=project_id, object_id="")
    prefixes[_.name] = _.uri
    for n,u in prefixes.items():
        r.bind(n, u)
    r = r.serialize()
    if isinstance(out, (str, Path)):
        out = Path(out)
        out.write_text(r)
        return out
    else:
        assert(out is None)
        return r


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
    
    def list():
        for n,q in queries.items():
            print('='*80)
            print(n+':')
            print('')
            print(q)
        return 

    
    from fire import Fire
    def default_substitutions(): return SPARQLQuery.defaults.substitutions
    Fire({f.__name__:f for f in {sparql, list, query, default_substitutions}})
