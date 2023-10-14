"""maybe generic query utils here"""


class Prefixes:
    def __init__(self, prefixes='default') -> None:
        if prefixes == 'default':
            from .queries import namespaces
            prefixes = namespaces()
        self.prefixes = prefixes
    
    def __iter__(self):
        yield from self.prefixes
    
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
                 prefixes='default',
                 constructbody = '?s ?p ?o.',
                 wherebody='?s ?p ?o.') -> None:
        if prefixes == 'default':
            from .queries import namespaces
            prefixes = namespaces()
        self.prefixes = prefixes
        self.constructbody = constructbody
        self.wherebody = wherebody

    # classmethod
    # def from_string 
    # parse a string
    # TODO:  
    
    # def known namespaces
    # TODO
    # def add known prefix
    # parse xxx: and add prefix from namespaces if not in given namespaces
        
    def __str__(self) -> str:
        _ = (
        f"{Prefixes()} \n\n\n"
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

