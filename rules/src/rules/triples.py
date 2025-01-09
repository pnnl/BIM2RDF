#https://github.com/RDFLib/OWL-RL/blob/master/owlrl/Closure.py
# the 'deepest' idea is:     Store(Graph) -f-> Store(Graph)
# gen rules...uggh tricky    Store(Graph) -f-> (Store(Graph) -f2-> Store(Graph)  )
# validation is 'adjacent'

from .abstract import abstract as b
import pyoxigraph as g
from typing import Iterable, Iterator


def canon(triples):
    # algo seems to gets stuck (slow?)
    # wait for update TODO
    from pyoxigraph import Dataset, CanonicalizationAlgorithm
    def _(triples):
        d = Dataset(g.Quad(*t) for t in triples)
        d.canonicalize(CanonicalizationAlgorithm.UNSTABLE) # ?? unstable??
        for q in d: yield q.triple
    return tuple(_(triples))

anon_uri = "urn:anon:hash:"
def canon(triples, ):
    import rdflib as r
    from functools import cache
    @cache
    def replace(n): # replace store
        if isinstance(n, r.BNode):
            return  f"<{anon_uri}{n}>"
        elif isinstance(n, r.Literal):
            return f'"{n}"'
        else:
            assert(isinstance(n, r.URIRef))
            return f"<{n}>"
    
    def to_cg(triples): 
        p = '.\n'.join(str(t) for t in triples)
        if not p: return r.Graph()
        from rdflib.compare import to_canonical_graph
        p = p+'.'
        _ = r.Graph().parse(data=p, format='ntriples')
        _ = to_canonical_graph(_)
        return _
    def rg2ogs(rg):
        # 'convert' rdflib graph to pyoxigraph store through serialization
        s = g.Store()
        if len(rg):
            _ = '.\n'.join(' '.join(map(replace, t)) for t in rg)+'.'
            s.bulk_load(_, format=g.RdfFormat.N_TRIPLES)
        return s
            
    _ = to_cg(triples)
    _ = rg2ogs(_)
    _ = tuple(q.triple for q in _)
    return _



class Triples(b.Data): # TODO: create something backed by TTL
    # peformance comparison of ~400,000 triples
    #In [41]: %timeit g.Store().bulk_load('data.ttl', 'text/turtle')
    #2.08 s ± 70.8 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    #In [26]: %timeit Store().bulk_extend(g.Quad(*t) for t in g.parse('data.ttl', 'text/turtle'   
    #...: ) )
    #2.89 s ± 78.6 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    # 27% faster

    def __init__(self, data: Iterable[g.Triple]=[]) -> None:
        if isinstance(data, self.__class__):
            self._data = data._data
        elif isinstance(data, Iterator):
            self._data = frozenset(data)
        else:
            assert(isinstance(data, Iterable  ))
            self._data = data
    
    def __len__(self) -> int:
        return len(self._data)
    def __bool__(self) -> bool:
        return True if len(self) else False

    def __iter__(self) -> Iterable[g.Triple]:
        yield from self._data
    
    def __add__(self, data: 'Triples' ) -> 'Triples':
        from itertools import chain 
        return Triples(chain(self._data, data._data))



class OxiGraph(b.DataBase):
    # __id__ if backed by files, there is a IDENTITY file
    
    def __init__(self, db: g.Store=g.Store()) -> None:
        self._store = db
    
    def __iter__(self) -> Iterable[g.Quad]:
        yield from self._store

    def __len__(self):
        return len(self._store)
    
    def __hash__(self) -> int:
        # return len(self._store)#  not strictly correct
        # return _
        _ = self._store
        # pyoxigraph doesn't hash the contents
        _ = frozenset(_)
        _ = hash(_)
        return _

    # on the query
    #def query(self, query: 'SelectQuery') -> 'SelectQueryData':
    #    _ = query(self)
    #    return _

    def insert(self, data: b.Data) -> None:
        data.insert(self)


class SelectQueryData(b.Data):
    def __init__(self, result: g.QuerySolutions | Iterable[g.QuerySolution] ) -> None:
        self._result = result

    def __iter__(self):
        yield from self._result

    def __add__(self, data: 'SelectQueryData') -> 'SelectQueryData':
        from itertools import chain
        return SelectQueryData(chain(self._result, data._result))
    
    def insert(self, db: OxiGraph) -> None:
        raise NotImplementedError
    

class SelectQuery(b.Query):

    def __init__(self, query: str) -> None:
        assert('select' in query.lower()) # TODO: need to programmatically check this
        self._query = query

    def __add__(self, query: 'SelectQuery') -> 'SelectQuery':
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self._query)

    def __call__(self, db: OxiGraph, **k) -> SelectQueryData:
        _ =  db._store.query(str(self),  **k)
        assert(isinstance(_, g.QuerySolutions))
        _ = SelectQueryData(_)
        return _


class ConstructQuery(b.Query):

    def __init__(self, query: str) -> None:
        assert('construct' in query.lower()) # TODO: need to programmatically check this
        self._query = query

    def __add__(self, query: 'ConstructQuery') -> 'ConstructQuery':
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self._query)

    def __call__(self, db: OxiGraph, **k) -> Iterable[g.Triple]:
        _ =  db._store.query(str(self),  **k)
        assert(isinstance(_, g.QueryTriples))
        yield from _


called = set() # [(rule, dbstate), ...]

class xCachedRuleCall:

    def __call__(self, db: OxiGraph) -> Iterable[g.Triple]:
        #h = hash((db)) 
        h = len(db) # risky
        call = (hash(self), h)
        if call in called:
            return Triples([]) # was already captured
        else:
            called.add(call)
            _ = self.do(db)
            return _


class RuleCall:
    def __call__(self, db:OxiGraph, **k) -> Iterable[g.Triple]:
        yield from self.do(db, **k)


class Rule(RuleCall, b.Rule):

    def __hash__(self) -> int:
        return hash(self.spec)
    meta_uri = 'http://meta'

    def add_star_meta(self, data: Iterable[g.Triple], deanon=False) -> Iterable[g.Triple]:
        meta = tuple(self.meta())
        if deanon:
            data = canon(data)
            meta = canon(meta)
        for t in data:
            yield t
            for m in meta:
                #    ('data'triple,    meta  ,   'meta'triple)
                yield g.Triple(t, g.NamedNode(self.meta_uri), m)
    

class ConstructRule(Rule):

    def __init__(self, spec: ConstructQuery) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> ConstructQuery:
        return self._spec

    def __add__(self, rule: 'Rule') -> 'Rules':
        return Rules([self, rule])

    def meta(self, ) -> Iterable[g.Triple]:
        # can add query str. or triples!
        # TODO
        yield from []

    def do(self, db: OxiGraph, deanon=False, ) -> Iterable[g.Triple]:
        _ = db._store.query(str(self.spec))
        assert(isinstance(_, g.QueryTriples))
        yield from self.add_star_meta(_, deanon=deanon)


from typing import Protocol, runtime_checkable
@runtime_checkable
class PyRuleCallable(Protocol):
    def __call__(self, db: OxiGraph) -> Triples:
        raise NotImplementedError
#Callable[[OxiGraph], Triples]

class PyRule(Rule):

    def __init__(self, spec: PyRuleCallable) -> None:
        self._spec = spec

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    @property
    def name(self):
        from inspect import getmodule
        mn = getmodule(self.spec).__spec__.name
        assert('__main__' not in mn)
        return f"{mn}.{self.spec.__name__}"
    
    @property
    def spec(self) -> PyRuleCallable:
        return self._spec
    
    def meta(self, ) -> Triples:
        # can add query str. or triples!
        return Triples([])
    
    def __add__(self, rule: 'Rule') -> 'Rules':
        return Rules([self, rule])
    
    def do(self, db: OxiGraph, deanon=False) -> Iterable[g.Triple]:
        _ = self.spec(db)
        yield from self.add_star_meta(_, deanon=deanon)


def _(db: OxiGraph): return Triples([])
noeffect_pyfunc: PyRuleCallable = _
noeffect_constructquery: ConstructQuery = ConstructQuery('construct ?s ?p ?o where {} limit 0')


Spec = PyRuleCallable | ConstructQuery
RulesSpec = Iterable[ Spec ]
Rule = PyRule | ConstructRule
class Rules(b.Rules):

    def __init__(self, rules: Iterator[Rule] ) -> None:
        self.rules = rules
    
    @property
    def spec(self) -> RulesSpec:
        return list(r.spec for r in self.rules)
    
    
    def __iter__(self) -> Iterator[Rule]:
        for r in self.rules: yield r


    def meta(self, data: Triples) -> Triples:
        # get the meta from each
        _ = map(lambda cr: cr.meta(data)._data, self)
        from itertools import chain
        _ = chain.from_iterable(_)
        return _


    def __add__(self, rules: 'Rules') -> 'Rules':
        _ = list(self.rules)+list(rules.rules)
        return Rules(_)
    
    def __call__(self, db: OxiGraph, **k) -> Triples:
        _ = map(lambda r: r(db, **k)._data, self.rules)
        from itertools import chain
        _ = chain.from_iterable(_)
        _ = Triples(_)
        return _


class Validation(b.Validation):
    ...


class Result(b.Result):
    def __init__(self, db: OxiGraph, result: b.Success | b.Failure ) -> None:
        self._db = db
        self._res = result
    
    def __bool__(self) -> b.Success | b.Failure:
        return self._res
    
    @property
    def db(self) -> OxiGraph:
        return self._db
    
    def __call__(self) -> OxiGraph:
        return self.db


import logging # :( i dont do module level imports
logger = logging.getLogger('engine')

class Engine(b.Engine): # rule app on Store

    def __init__(self, rules: Rules, db: OxiGraph,
                 MAX_ITER=999,
                 deanon=True,
                 log=True, print_log=True,
                 ) -> None:
        self._rules = rules
        self._db = db
        self.MAX_ITER = MAX_ITER
        self.deanon = deanon
        self.i = 0
        
        # logging
        if log:
            from collections import defaultdict, namedtuple
            from types import SimpleNamespace as NS
            self.logging = NS(
                print = print_log,
                log = defaultdict(list),
                delta = namedtuple('delta', ['before', 'after'] ))

    @property
    def rules(self) -> Rules:
        return self._rules
    
    @property
    def db(self) -> OxiGraph:
        return self._db
    
    def validate(self) -> Result:
        if hasattr(self, 'logging'):
            logger.info('validating')
        raise NotImplementedError
    
    def crank_once(self) -> OxiGraph:
        if hasattr(self, 'logging'):
            if self.logging.print:
                line = '-'*10
                logger.info(f"CYCLE {self.i} {line}")

        for r in self.rules: # TODO: could be parallelized
            # before
            if hasattr(self, 'logging'):
                before = len(self.db)
                if self.logging.print:
                    logger.info(f"{repr(r)}")
                from time import monotonic
                start_time = monotonic()

            # do
            _ = r(self.db, deanon=self.deanon)
            self.db._store.bulk_extend(g.Quad(*t) for t in _)
            del _

            # after
            if hasattr(self, 'logging'):
                delta = self.logging.delta(before, len(self.db))
                self.logging.log[r.spec].append(delta)
                if self.logging.print:
                    logger.info(f"# triples before {delta.before }, after {delta.after } => {delta.after-delta.before}.")
                    logger.info(f"took {'{0:.2f}'.format(monotonic()-start_time)} seconds")
        
        self.i += 1
        self.db._store.flush()
        self.db._store.optimize()
        return self.db

    def stop(self) -> bool:
        if self.MAX_ITER <= 0:
           return False
        # could put validations here
        if len(self.db) == len(self.crank_once()):
            return True
        else:
            return False
    
    def __iter__(self) -> Iterable[OxiGraph]:
        while (not self.stop()):
            if self.i >= self.MAX_ITER:
                if hasattr(self, 'logging'):
                    if self.logging.print:
                        logger.warning('reached max iter')
                break
            yield self.db
        else: # for case when nothing needs to happen
            yield self.db

    def final(self) -> OxiGraph:
        for _ in self: continue
        return self.db
    
    def __call__(self) -> Result:
        db = self.final()
        return Result(db, True)


