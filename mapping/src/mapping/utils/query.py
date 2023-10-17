"""maybe generic query utils here"""
from ontologies import namespace

class Prefixes:
    def __init__(self, prefixes=(), check_unique=True) -> None:
        from rdflib import URIRef
        _ = (namespace(p,URIRef(u)) for p,u in prefixes) # normalize
        _ = frozenset(_)
        if check_unique:
            if len(frozenset(p for p,_ in _)) != len(_):
                raise ValueError('prefixes not unique')
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
        assert(name)
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
class SelectQuery:#(base class in engine)
    def __init__(self, *,
                 comments='',
                 prefixes=Prefixes(),
                 variables =(Variable('s'), Variable('p'), Variable('o') ),
                 wherebody='?s ?p ?o.') -> None:
        self.prefixes = Prefixes(prefixes)
        self.variables = variables
        self.wherebody = wherebody
        self.comments = comments
    
    @classmethod
    def parse(cls, s: str):
        from re import findall, IGNORECASE, DOTALL
        ps = findall("prefix (?P<prefix>.*?)\s*:\s*<(?P<uri>.*)>", s, IGNORECASE)
        ps = Prefixes(namespace(p,u) for p,u in ps) + known_prefixes
        vs = findall("select(.*)where", s, IGNORECASE | DOTALL )
        vs = vs[0].strip()
        vs = findall("\?(?P<var>\S*)", s, )
        vs = map(Variable, vs)
        vs = tuple(vs)
        w = findall("where\s*\n*{(?P<wherebody>.*?)}", s, IGNORECASE | DOTALL )
        w = w[0].strip()
        up = findall("(?P<usedprefix>[a-z|A-Z|.|0-9]*):.*?", '\n'.join(l for l in (w).split('\n') if not l.strip().startswith('#')  ), )
        up = frozenset(up)
        def_prefixes = {p for p,_ in ps}
        for p in up:
            if p not in def_prefixes:
                raise ValueError(f'{p} not defined')
        # trim prefixes: only create if it's used or known
        ps = Prefixes(namespace(p, str(u) ) for p,u in ps if p in up)
        return cls(
            comments='\n'.join(l.strip() for l in s.split('\n') if not ( (l.strip() in w) ) and l.strip().startswith('#')  ),
            prefixes=ps,
            variables=vs,
            wherebody=w,)
        
    def __str__(self) -> str:
        _ = (
        f"{self.comments} \n"
        f"{self.prefixes} \n\n\n"
        f"SELECT "
        f"{' '.join(str(v) for v in self.variables) }"
        " WHERE { \n"
        f"{self.wherebody} \n"
        "}" )
        _ = _.strip()
        _ = _.strip('\n')
        return _

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
        ps = findall("prefix (?P<prefix>.*?)\s*:\s*<(?P<uri>.*)>", s, IGNORECASE)
        ps = Prefixes(namespace(p,u) for p,u in ps) + known_prefixes
        c = findall("construct\s*\n*{(?P<constructbody>.*?)}", s, IGNORECASE | DOTALL )
        c = c[0].strip()
        w = findall("where\s*\n*{(?P<wherebody>.*?)}", s, IGNORECASE | DOTALL )
        w = w[0].strip()
        up = findall("(?P<usedprefix>[a-z|A-Z|.|0-9]*):.*?", '\n'.join(l for l in (c+'\n'+w).split('\n') if not l.strip().startswith('#')  ), )
        up = frozenset(up)
        def_prefixes = {p for p,_ in ps}
        for p in up:
            if p not in def_prefixes:
                raise ValueError(f'{p} not defined')
        # trim prefixes: only create if it's used or known
        ps = Prefixes(namespace(p, str(u) ) for p,u in ps if p in up)
        return cls(
            comments='\n'.join(l.strip() for l in s.split('\n') if not ((l.strip() in c) or (l.strip() in w)) and l.strip().startswith('#')  ),
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
        _ = _.strip()
        _ = _.strip('\n')
        return _


def parse(s: str):
    # "proper" way is to use a parser
    es = {}
    try: # trying this first bc it's more common in the project
        return ConstructQuery.parse(s)
    except Exception as e:
        es['construct'] = e
    try:
        return SelectQuery.parse(s)
    except Exception as e:
        es['select'] = e
    raise ValueError(f'could not interpret query. {es}')


def make_regex_parts(parts):
    for part in parts:
        for po in ('p', 'o'):
            #       uri cast as string so that regex can be applied
            yield f"""regex(str(?{po}), "{part}")"""


def parse_files(file_or_dir, ):
    from pathlib import Path
    p = Path(file_or_dir); del file_or_dir
    assert(p.exists())
    def write(f):
        _ = f.open().read()
        _ = parse(_)
        _ = str(_)
        open(f, 'w').write(_)
        return p
    if p.is_dir():
        for f in p.glob('**/*.rq'):
            write(f,)
    else:
        assert(p.is_file())
        write(p)


if __name__ == '__main__':
    import fire
    fire.Fire({
        'prefixes': lambda: known_prefixes,
        'parse_files': parse_files,
          } )

