base_uri = lambda:  "http://speckle.systems/"


def contextualize(d: dict) -> dict:
    d = d.copy()
    context = {
        '@vocab':       base_uri(),
        '@base':        base_uri(),
        'id':           '@id',
        }
    # assumption: keys are consistantly lists
    from .objects import find_list_fields
    for lf in find_list_fields(d): context[lf] = {"@container": "@list"}; del lf
    if isinstance(d, dict):
        d['@context'] =  context
    elif isinstance(d, list):
        d = {'@context': context, '@graph': d} 
    return d


def rdf(d):
    _ = d
    _ = contextualize(_)
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

