# hacks applicable to pyshacl inferencing.
from rdflib import (Literal,
Graph as _Graph,
ConjunctiveGraph as _ConjunctiveGraph,
Dataset as _Dataset,
)
from rdflib.plugins.stores.memory import Memory
class _:
    def __init__(self, *p, **k):
        self._offensive = set()
        super().__init__(*p, **k)
    
    def add(self, t):
        if isinstance(t[0], Literal):
            self._offensive.add(t)
        # so that it keeps working as usual
        if isinstance(self.store, Memory):
            return super().add(t)
        # not tolerable otherwise
    
    def clean(self):
        if isinstance(self.store, Memory):
            it = (d for d in self if d not in self._offensive)
            _ = self.__class__()
            for tq in it: _.add(tq)
            return _
        else:
            return self  # already clean


class Graph(_, _Graph): pass
class ConjunctiveGraph(_, _ConjunctiveGraph): pass
class Dataset(_, _Dataset): pass
