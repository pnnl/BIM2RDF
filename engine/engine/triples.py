#https://github.com/RDFLib/OWL-RL/blob/master/owlrl/Closure.py
# the 'deepest' idea is:     Store(Graph) -f-> Store(Graph)
# gen rules...uggh tricky    Store(Graph) -f-> (Store(Graph) -f2-> Store(Graph)  )
# validation is 'adjacent'

from .abstract import abstract as b
import pyoxigraph as g
from typing import Iterable, Iterator, Callable
# meta/rdfstar inserstion somewhere TODO


class Triples(b.Data):

    def __init__(self, data: Iterable[g.Triple]) -> None:
        self._data = data

    def __iter__(self) -> Iterable[g.Triple]:
        yield from self._data

    def __add__(self, data: 'Triples' ) -> 'Triples':
        from itertools import chain 
        return Triples(chain(self._data, data._data))

    def insert(self, db: 'OxiGraph', graph=None ) -> None:
        from io import BytesIO
        fmt='application/n-triples'
        _ = BytesIO() 
        g.serialize(self._data, _, fmt)
        _.seek(0)
        if len(_.getbuffer()):
            db._store.bulk_load(_, fmt, to_graph=graph)


class OxiGraph(b.DataBase):
    
    def __init__(self, db: g.Store) -> None:
        self._store = db
    
    def __iter__(self) -> Iterable[g.Quad]:
        yield from self._store

    def __len__(self):
        return len(self._store)

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

# could generate via sparql construct or python

class ConstructRule(b.Rule):

    def __init__(self, spec: ConstructQuery) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> ConstructQuery:
        return self._spec

    def __add__(self, rule: 'ConstructRule') -> 'ConstructRules':
        return ConstructRules([self.spec, rule.spec])
    
    def const_meta(self) -> Triples:
        # something that doesn't depend on the data
        return Triples([])

    def meta(self, data: Triples) -> Triples:
        # can add query str. or triples!
        # TODO
        return Triples([])

    def __call__(self, db: OxiGraph) -> Triples:
        _ = db._store.query(str(self.spec))
        assert(isinstance(_, g.QueryTriples))
        #yield from _
        return Triples(_)


class ConstructRules(b.Rules):
    def __init__(self, spec: Iterable[ConstructQuery]) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> Iterable[ConstructQuery]:
        return self._spec
    #queries:  = spec complaint
    #            Iterable[ConstructQuery] complaint

    def __iter__(self) -> Iterator['ConstructRule']:
        yield from map(lambda s: ConstructRule(s), self.spec)

    def __add__(self, rules: 'ConstructRules | ConstructRule') -> 'ConstructRules':
        if isinstance(rules, ConstructRule):
            rule = rules
            rules = ConstructRules([rule.spec])
        return ConstructRules(list(self.spec) + list(rules.spec) )
    
    def meta(self, data: Triples) -> Triples:
        _ = map(lambda cr: cr.meta(data)._data, self)
        from itertools import chain
        _ = chain.from_iterable(_)
        _ = Triples(_)
        return _
    
    def __call__(self, db: OxiGraph) -> Triples:
        _ = map(lambda q: q(db)._data, self.spec)
        from itertools import chain
        _ = chain.from_iterable(_)
        _ = Triples(_)
        return _


from typing import Protocol, runtime_checkable
@runtime_checkable
class PyRuleCallable(Protocol):
    def __call__(self, db: OxiGraph) -> Triples:
        ...
#Callable[[OxiGraph], Triples]

class PyRule(b.Rule):

    def __init__(self, spec: PyRuleCallable) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> PyRuleCallable:
        return self._spec
    
    def meta(self, data: Triples) -> Triples:
        # can add query str. or triples!
        return Triples([])
    
    def __add__(self, rule: 'PyRule') -> 'PyRules':
        return PyRules([self.spec, rule.spec])
    
    def __call__(self, db: OxiGraph) -> Triples:
        _ = self.spec(db)
        return _

def _idf(db: OxiGraph): return Triples([])
idf: PyRuleCallable = _idf
NoEffect = PyRule(idf)

class PyRules(b.Rules):

    def __init__(self, spec: Iterable[PyRuleCallable]) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> Iterable[PyRuleCallable]:
        return self._spec

    def __iter__(self) -> Iterator[PyRule]:
        _ = map(lambda r: PyRule(r) , self.spec)
        return _
    
    def __add__(self, rules: 'PyRules') -> 'PyRules':
        _ = list(self) + list(rules)
        return PyRules(_)
    
    def meta(self, data: Triples) -> Triples:
        _ = map(lambda cr: cr.meta(data)._data, self)
        from itertools import chain
        _ = chain.from_iterable(_)
        _ = Triples(_)
        return _
    
    def __call__(self, db: OxiGraph) -> Triples:
        _ = map(lambda c: PyRule(c)(db)._data, self.spec)
        from itertools import chain
        _ = chain.from_iterable(_)
        _ = Triples(_)
        return _



# can probably delete PyRules and ContructRules TODO

Spec = PyRuleCallable | ConstructQuery
RulesSpec = Iterable[ Spec ]
Rule = PyRule | ConstructRule
class Rules(b.Rules):

    def __init__(self, spec: RulesSpec) -> None:
        self._spec = spec
    
    @property
    def spec(self) -> RulesSpec:
        return list(self._spec)
    
    @classmethod
    def spec2rule(cls, s: Spec) -> Rule:
        if isinstance(s, PyRuleCallable): # :/
            return PyRule(s)
        elif isinstance(s, ConstructQuery):
            return ConstructRule(s)
        else:
            raise TypeError('unknown rule type')
    
    def __iter__(self) -> Iterator[Rule]:
        for s in self.spec:
            _ = self.spec2rule(s)
            yield _

    def meta(self, data: Triples) -> Triples:
        _ = map(lambda cr: cr.meta(data)._data, self)
        from itertools import chain
        _ = chain.from_iterable(_)
        _ = Triples(_)
        return _

    def __add__(self, rule: 'Rules') -> 'Rules':
        from itertools import chain
        _ = chain(self.spec, rule.spec)
        _ = list(_)
        return Rules(_)
    
    def __call__(self, db: OxiGraph) -> Triples:
        _ = map(lambda c: self.spec2rule(c)(db)._data, self.spec)
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


class Engine(b.Engine): # rule app on Store

    def __init__(self, rules: Rules, db: OxiGraph) -> None:
        self._rules = rules
        self._db = db

    @property
    def rules(self) -> Rules:
        return self._rules
    
    @property
    def db(self) -> OxiGraph:
        return self._db
    
    def validatation(self) -> Validation:
        raise NotImplementedError
    
    def crank_once(self) -> OxiGraph:
        #_ = map(lambda r: r(self.db), self.rules)
        #from itertools import chain
        #_ = chain.from_iterable(_)
        #_: Iterable[g.Triple] = chain.from_iterable(_)
        # _.insert(self.db)
        for r in self.rules:
            _ = r(self.db)
            _.insert(self.db)
        return self.db

    def stop(self) -> bool:
        # could put validations here
        if len(self.db) == len(self.crank_once()):
            return True
        else:
            return False
    
    def __iter__(self) -> Iterable[OxiGraph]:
        MAX_ITER = 999
        i = 0
        while (not self.stop()):
            if i > MAX_ITER: break
            yield self.db
            i += 1
        else: # for case when nothing needs to happen
            yield self.db

    def final(self) -> OxiGraph:
        from collections import deque
        def tail(n, iterable):
            "Return an iterator over the last n items"
            # tail(3, 'ABCDEFG') --> E F G
            return iter(deque(iterable, maxlen=n))
        _ = tail(1, self)
        _ = tuple(_)
        _ = _[0]
        return _
    
    def __call__(self) -> Result:
        #try:
        db = self.final()
        return Result(db, True)
        #except:
        #    sdf
        #    return Result(self.db, False)



def test():

    def _data(db: OxiGraph) -> Triples:
        _ = b'<http://example.com> <http://example.com/p> "1" .\n'
        _ = g.parse(_, 'text/turtle')
        _ = Triples(_)
        return _
    Data = PyRule(_data)
    _ = """
    construct {
        <http://example.com/a> <http://www.w3.org/2000/01/rdf-schelabel> "something" .}
    where {  }
    """
    Construct = ConstructQuery(_)
    rules = Rules([NoEffect, Data, Construct])
    engine = Engine(rules, OxiGraph(g.Store()) )
    res = engine()
    _ = res.db
    _ = list(_)
    return _


# sparql can be 'data', rule,

# axioms/data: .ttl
# apply 'rules': construct
# 'validation': sparql ask
# python funcs take store and return store.


if __name__ == '__main__':
    # consume dir for data
    ...
