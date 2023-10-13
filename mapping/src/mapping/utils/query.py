"""maybe generic query utils here"""


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
        def turi(uri):
            uri = str(uri)
            if not uri.startswith('<'):
                uri = f"<{uri}>"
                return uri
            else:
                return uri
        prefixes = '\n'.join(f"PREFIX {p.prefix}: {turi(p.uri)}" for p in self.prefixes)
        _ = (
        f"{prefixes} \n\n\n"
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

