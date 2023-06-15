# object data


import jsonpath_ng as jp
from types import SimpleNamespace as NS
# just use lenses/optics?
parsing = NS(
    fields = jp.parse("$..*"),     # recursive
    ids = jp.parse("$..id"),       # useful for extracting out objs...
    id_refs = jp.parse("$..referencedId"),
    # ...relations could be extracted b/c match results are nested DatumInContext.context -> DatumInContext
    jsonld = NS(**{k: jp.parse(f"$..{k}") for k in {'id', 'type', 'value'}}) # there's also speckle_type
)


def find_list_fields(d: dict):
    #d = {'n': 3, 'nested': {'nl': [], 'n':3 } }

    for m in parsing.fields.find(d):
        k = str(m.path)
        if isinstance(m.value, list):
            yield k


def sample_json():
    _ = open('.json').read()
    import json
    _ = json.loads(_)
    return _

def remove_at(d: dict) -> dict:
    # can't have @. collides with jsonld.
    # need copy? functional programming rules
    d = d.copy()
    for m in parsing.fields.find(d):
        k = str(m.path)
        if k.startswith('@'):
            _ = m.context.value.pop(k)
            m.context.value[k[1:]] = _ # is this ok? channging while iterating
    return d

def url_quote(d: dict) -> dict:
    from urllib.parse import quote 
    d = d.copy()
    for m in parsing.fields.find(d):
        k = str(m.path)
        v = m.context.value.pop(k)
        k = quote(k)
        m.context.value[k] = v # is this ok? channging while iterating
    return d


from . import base_uri

def contextualize(d: dict) -> dict:
    #"@context": {"@vocab": "http://speckle.systems/", "@base":"http://speckle.systems/", "id": "@id", "referencedId": "@id" },
    # this works in jsonld playground
    d = d.copy()
    context = {
        '@vocab':       base_uri(),
        '@base':        base_uri(),
        'referencedId': '@id',
        'id':           '@id',
        #"data":         {"@container": "@list"}  # assumption: all data keys are lists!
        }
    # assumption: keys are consistantly lists
    for lf in find_list_fields(d): context[lf] = {"@container": "@list"}; del lf
    if isinstance(d, dict):
        d['@context'] =  context
    elif isinstance(d, list):
        #d.insert(0, {'@context': context})
        d = {'@context': context, '@graph': d} 
    #d['@context']['id'] = '@id'
    # speckle specific
    return d


def test():
    _ = {
            'id':'o1', # ok maybe just take this id as speckle and reinterpret as schema.org/id
            'Outside': 'sdf',
            '@inside': [
                {'id': 'i1', 
                'p': 3},
                [{'referencedId': 'rid', 'speckle_type': 'reference' }],
                {'referencedId': 'rid2', 'speckle_type': 'reference' },
            ]
        }
    _ = sample_json()
    _ = remove_at(_)
    _ = id_(_) 
    _ = contextualize(_) # context after other stuff
    #return _
    from pyld import jsonld as lj
    _ = lj.flatten(_, )#contextualize({})['@context'])
    _ = lj.to_rdf(_, options=NS(format='application/n-quads').__dict__ ) #close to flatten
    import rdflib
    _ = rdflib.Graph().parse(data=_, format='nquads')
    return _
    #_ = lj.expand(_, )# NS(graph=True).__dict__ )
    #_ = lj.flatten(_, contextualize({})['@context']  ) # creates @graph
    return _


# can take json or speckleid
def rdf(d):
    # now just map? can make bnode a subject?
    _ = {
            'id':'o1', # ok maybe just take this id as speckle and reinterpret as schema.org/id
            'Outside': 'sdf',
            'inside': [
                {'id': 'dataid', 'data': list(range(3))+list(range(3))  }, # assumes set w/o @container:@list
                {'id': 'i1', 
                'p': 3},
                {'referencedId': 'rid', 'speckle_type': 'whatever' }, 
                {'id': 'i2', 
                'p': 4}
            ]
        }
    #_ = sample_json()
    _ = d
    _ = remove_at(_)
    _ = url_quote(_)
    _ = contextualize(_)
    #from pyld import jsonld as lj
    #_ = lj.flatten(_)
    #lj.to_rdf()
    # _ = lj.to_rdf()
    #     _,
    #     options=NS(
    #     format='application/n-quads',
    #     produceGeneralizedRdf=True).__dict__ ) #
    # PROBLEM: only produces triples that are identified in @context
    # doesn't seem to be responding to @vocab
    # maybe not compliant!
    from rdflib import Graph
    from json import dumps
    _ = dumps(_)
    _ = Graph().parse(data=_, format='json-ld')
    from io import BytesIO
    o = BytesIO()
    _ = _.serialize(o, 'text/turtle')
    o.seek(0)
    _ = o
    return _


if __name__ == '__main__':
    ...


