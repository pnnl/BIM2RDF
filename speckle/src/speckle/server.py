
base_uri = lambda: 'http://speckle.systems/server/'


def contextualize(d):
    _ = d.copy()
    # TODO: this really should come from the schema
    _['@context'] = {'@vocab': base_uri(), }
    return _


def rdf(d: dict):
    _ = contextualize(d)
    from pyld import jsonld as lj
    _ = lj.flatten(_, )#contextualize({})['@context']) 
    from types import SimpleNamespace as NS
    _ = lj.to_rdf(_, options=NS(format='application/n-quads').__dict__ ) #close to flatten
    return _

def test():
    from .graphql import queries, query
    _ = queries().streams
    _ = query(_)
    _ = rdf(_)
    return _


def apikey():
    from pathlib import Path
    _ = Path(__file__).parent / '..' / '..' / 'secret.json'
    _ = open(_)
    import json
    _  = json.load(_)
    _ = _['speckl_token']
    return _



