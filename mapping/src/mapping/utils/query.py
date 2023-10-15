"""maybe generic query utils here"""

from ontologies import namespace

class Prefixes:
    def __init__(self, prefixes=()) -> None:
        from rdflib import URIRef
        _ = (namespace(p,URIRef(u)) for p,u in prefixes) # normalize
        _ = frozenset(_)
        _ = sorted(_, key=lambda ns:ns.prefix)
        _ = tuple(_)
        self.prefixes = _
    
    def __iter__(self):
        yield from self.prefixes
    
    def __add__(self, o):
        return Prefixes(list(self)+list(o))
    
    def __str__(self) -> str:
        def turi(uri):
            uri = str(uri)
            if not uri.startswith('<'):
                uri = f"<{uri}>"
                return uri
            else:
                return uri
        _ = '\n'.join(f"PREFIX {p.prefix}: {turi(p.uri)}" for p in self.prefixes)
        return _

from .queries import namespaces
known_prefixes = Prefixes(list(namespaces()))

class Variable:
    def __init__(self, name) -> None:
        self.name = name
    def __str__(self) -> str:
        return f"?{self.name}"

class Node:
    def __init__(self, prefix, name) -> None:
        self.prefix = prefix
        self.name = name
    
    def variable_(self, i=0):
        return Variable(f"{self.name}{str(i) if i else ''}")
    var_ = variable_
    @property
    def variable(self): return self.variable_()
    var = variable
    
    def __str__(self) -> str:
        return f"{self.prefix}:{self.name}"


# base class might be better in 'engine'
class ConstructQuery:#(base class in engine)
    def __init__(self, *,
                 comments='',
                 prefixes=Prefixes(),
                 constructbody = '?s ?p ?o.',
                 wherebody='?s ?p ?o.') -> None:
        self.prefixes = Prefixes(prefixes)
        self.constructbody = constructbody
        self.wherebody = wherebody
        self.comments = comments

    @classmethod
    def parse(cls, s: str):
        from re import findall, IGNORECASE, DOTALL
        _ = findall("prefix (?P<prefix>.*?)\s*:\s* <(?P<uri>.*)>", s, IGNORECASE)
        ps = Prefixes(namespace(p,u) for p,u in _) + known_prefixes
        c = findall("construct\s*\n*{(?P<constructbody>.*?)}", s, IGNORECASE | DOTALL )
        c = c[0]
        w = findall("where\s*\n*{(?P<wherebody>.*?)}", s, IGNORECASE | DOTALL )
        w = w[0]
        up = findall("(?P<usedprefix>[a-z|0-9|.|A-Z|_]*):.*?", c+'\n'+w, )
        up = frozenset(up)
        def_prefixes = {p for p,_ in ps}
        for p in up:
            if p not in def_prefixes:
                raise ValueError(f'{p} not defined')
        # trim prefixes: only create if it's used or known
        ps = Prefixes(namespace(p, str(u) ) for p,u in ps if p in up)
        return cls(
            comments='\n'.join(l.strip() for l in s.split('\n') if not ((l in str(ps)) or (l in c) or (l in w) ) and l.strip().startswith('#')  ),
            prefixes=ps,
            constructbody=c,
            wherebody=w,)
        
    def __str__(self) -> str:
        _ = (
        f"{self.comments} \n"
        f"{self.prefixes} \n\n\n"
        "CONSTRUCT { \n"
        f"{self.constructbody} \n"
        "} \n"
        "WHERE { \n"
        f"{self.wherebody} \n"
        "}" )
        return _


def make_regex_parts(parts):
    for part in parts:
        for po in ('p', 'o'):
            #       uri cast as string so that regex can be applied
            yield f"""regex(str(?{po}), "{part}")"""


if __name__ == '__main__':
    import fire
    fire.Fire({'prefixes': lambda: str(Prefixes()) } )

