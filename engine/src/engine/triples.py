#https://github.com/RDFLib/OWL-RL/blob/master/owlrl/Closure.py
# the 'deepest' idea is:     Store(Graph) -f-> Store(Graph)
# gen rules...uggh tricky    Store(Graph) -f-> (Store(Graph) -f2-> Store(Graph)  )
# validation is 'adjacent'

from .abstract import abstract as b
import pyoxigraph as g
from typing import Iterable, Iterator
# meta/rdfstar inserstion somewhere TODO


def it():
    i = 0
    while True:
        yield i
        i += 1


# anon nodes break the repeatability
# so this is a cache that associates
# hash(namednodes) -> blanknodes
deanoned = {}


class Triples(b.Data):

    def __init__(self, data: Iterable[g.Triple]=[]) -> None:
        if not isinstance(data, (tuple, list, set, frozenset)):
            self._data = tuple((data))
        else:
            self._data = data
    
    def __hash__(self) -> int:
        return hash((self._data))
    
    def __len__(self) -> int:
        i = 0
        for _ in self: i += 1
        return i

    def __iter__(self) -> Iterable[g.Triple]:
        yield from self._data

    def __add__(self, data: 'Triples' ) -> 'Triples':
        from itertools import chain 
        return Triples(chain(self._data, data._data))
    
    def known_hash(self) -> str:
        # a hash based on the content. assumed to persist.
        if not self._data: return ''
        def tohash(triples):
            # hash the 'constants' to id the set of triples.
            # ...not the ones that can potentially change
            for spo in triples:
                for _ in spo:
                    if isinstance(_, g.BlankNode):
                        continue
                    if str(_.value).startswith(self.deanon_uri):
                        continue
                    yield _

        # do i need a hashing library??
        from hashlib import md5 # md5 instead of __hash__ bc hash() changes bw program launches
        tohash = (str(t.value) for t in tohash(self._data))
        tohash = sorted(tohash)
        tohash = ''.join(t for t in tohash)
        tohash = tohash.encode()
        tohash = md5(tohash)
        tohash = tohash.hexdigest()
        return tohash
    
    def anons(self):
        for triple in self:
            if any(map(lambda _: isinstance(_, g.BlankNode) , triple)):
                yield triple

    def deanon(self) -> 'Triples':
        # block newly generated anon nodes if they've already been seen.
        # the 'id' is the context of named nodes in the triples 'batch'.
        id = self.known_hash()
        if not id: return Triples()
        
        if id in deanoned:
            da = deanoned[id]
            nn = []
            for triple in self:
                if all(map(lambda _: not isinstance(_, g.BlankNode) , triple)):
                    nn.append(triple)
        else:
            da = []
            nn = []
            for triple in self:
                if any(map(lambda _: isinstance(_, g.BlankNode) , triple)):
                    da.append(triple)
                else:
                    nn.append(triple)
            deanoned[id] = tuple(da)

        r = self.__class__(nn) + self.__class__(da)
        return r
    deanon_uri = 'http://deanon' # {id}
    def _deanon(self) -> 'Triples':
        # not sure this is correct
        id = self.known_hash()
        if not id: return Triples()
        url = f'{self.deanon_uri}/{id}'
        iz = iter(it())
        
        if id in deanoned:
            da = deanoned[id]
            nn = []
            for triple in self:
                if all(map(lambda _: not isinstance(_, g.BlankNode) , triple)):
                    nn.append(triple)
        else:
            da = []
            nn = []
            for triple in self:
                if any(map(lambda _: isinstance(_, g.BlankNode) , triple)):
                    s, p, o = triple
                    s = g.NamedNode(f"{url}/{next(iz)}") if isinstance(s, g.BlankNode) else s
                    p = g.NamedNode(f"{url}/{next(iz)}") if isinstance(p, g.BlankNode) else p
                    o = g.NamedNode(f"{url}/{next(iz)}") if isinstance(o, g.BlankNode) else o
                    triple = g.Triple(s, p, o)
                    da.append(triple)
                else:
                    nn.append(triple)
            deanoned[id] = tuple(da)

        r = self.__class__(nn) + self.__class__(da)
        return r
    

    def insert(self, db: 'OxiGraph', graph=g.DefaultGraph()) -> None:
        if len(self):
            db._store.bulk_extend(g.Quad(*t) for t in self)
            db._store.optimize()


class OxiGraph(b.DataBase):
    
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

    def __call__(self, db: OxiGraph, **k) -> Triples:
        _ =  db._store.query(str(self),  **k)
        assert(isinstance(_, g.QueryTriples))
        _ = Triples(_)
        return _


called = set() # [(rule, dbstate), ...]

class CachedRuleCall:

    def __call__(self, db: OxiGraph) -> Triples:
        #h = hash((db)) # len(db) is risky
        h = len(db)
        call = (hash(self), h)
        if call in called:
            return Triples([]) # was already captured
        else:
            called.add(call)
            _ = self.do(db)
            return _

        
class Rule(CachedRuleCall, b.Rule):

    def __hash__(self) -> int:
        return hash(self.spec)
    meta_uri = 'http://meta'

    def add_meta(self, data: Triples) -> Triples:
        def nest(data):
            _ = self.meta(data)
            _ = Triples(_)
            _ = _.deanon()
            ms = _
            if ms: # metas
                for t in data:
                    for m in ms:
                        #            ('data'triple,    meta  ,   'meta'triple)
                        yield g.Triple(t, g.NamedNode(self.meta_uri), m)
            yield from data
        _ = nest(data)
        _ = Triples(_)
        return _
    

class ConstructRule(Rule):

    def __init__(self, spec: ConstructQuery) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> ConstructQuery:
        return self._spec

    def __add__(self, rule: 'Rule') -> 'Rules':
        return Rules([self, rule])
    
    def const_meta(self) -> Triples:
        # something that doesn't depend on the data
        return Triples([])

    def meta(self, data: Triples) -> Triples:
        # can add query str. or triples!
        # TODO
        return Triples([])

    def do(self, db: OxiGraph) -> Triples:
        _ = db._store.query(str(self.spec))
        assert(isinstance(_, g.QueryTriples))
        _ = Triples(_)
        _ = _.deanon()
        _ = self.add_meta(_) 
        return _


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
    
    def meta(self, data: Triples) -> Triples:
        # can add query str. or triples!
        return Triples([])
    
    def __add__(self, rule: 'Rule') -> 'Rules':
        return Rules([self, rule])
    
    def do(self, db: OxiGraph) -> Triples:
        _ = self.spec(db)
        _ = Triples(_)
        _ = _.deanon()
        _ = self.add_meta(_)
        return _


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
    
    def __call__(self, db: OxiGraph) -> Triples:
        _ = map(lambda r: r(db)._data, self.rules)
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

    def __init__(self, rules: Rules, db: OxiGraph, MAX_ITER=999,
                 log=True, print_log=True,
                 ) -> None:
        self._rules = rules
        self._db = db
        self.MAX_ITER = MAX_ITER
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

        for r in self.rules:
            # before
            before = len(self.db)
            if hasattr(self, 'logging'):
                if self.logging.print:
                    logger.info(f"{repr(r)}")

            # do
            _ = r(self.db)
            _.insert(self.db)

            # after
            if hasattr(self, 'logging'):
                delta = self.logging.delta(before, len(self.db))
                self.logging.log[r.spec].append(delta)
                if self.logging.print:
                    logger.info(f"# triples before {delta.before }, after {delta.after } => {delta.after-delta.before}")
        
        self.i += 1
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


if __name__ == '__main__':
    # consume dir for data
    ...
