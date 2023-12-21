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


def remove_at(d: dict) -> dict:
    # can't have @. collides with jsonld.
    # need copy? functional programming rules
    # d = d.copy()
    for m in parsing.fields.find(d):
        k = str(m.path)
        if k.startswith('@'):
            _ = m.context.value.pop(k)
            m.context.value[k[1:]] = _ # is this ok? channging while iterating
    return d


def url_quote(d: dict) -> dict:
    from urllib.parse import quote 
    # d = d.copy()
    for m in parsing.fields.find(d):
        k = str(m.path)
        # parens add an extra quotation.
        # str(m.path.__class__('sdf()'))
        # "'sdf()'"
        k = k.strip("'")
        v = m.context.value.pop(k)
        k = quote(k)
        m.context.value[k] = v # is this ok? channging while iterating
    return d


from . import base_uri

def contextualize(d: dict) -> dict:
    #"@context": {"@vocab": "http://speckle.systems/", "@base":"http://speckle.systems/", "id": "@id", "referencedId": "@id" },
    # this works in jsonld playground
    #d = d.copy()
    context = {
        '@vocab':       base_uri(),
        '@base':        base_uri(),
        'referencedId': '@id',
        'id':           '@id',
        #"data":         {"@container": "@list"} most (almost all?) of these are the data lists
        }
    #    make lists rdf lists
    for lf in find_list_fields(d):
        context[lf] = {"@container": "@list"}; del lf
    # perhaps there might be just one list keyed as 'data' close to the root...
    # ..but then encode_data_lists handles the majority of cases where
    # the lists have the coord data.
    if isinstance(d, dict):
        d['@context'] =  context
    elif isinstance(d, list):
        #d.insert(0, {'@context': context})
        d = {'@context': context, '@graph': d} 
    #d['@context']['id'] = '@id'
    # speckle specific
    return d

def encode_data_lists(d: dict, encoder=lambda l: "") -> dict:
    # need copy? functional programming rules
    # d = d.copy()
    for m in parsing.fields.find(d):
        k = str(m.path)
        if k == 'data':
            _ = m.context.value[k]
            if not (isinstance(_, list)): # like stream/object/data
                continue
            else:
                assert(isinstance(_, list))
                if not all(isinstance(i, (int, float)) for i in _):
                #if _ == # [["Key Name", "Comments"]]: # some exception that showed up.
                # [["Lighting Fixture Schedule", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""], ["Lighting Control Zone ID", "Daylight Harvesting Sequence Designation
                    continue
                assert(m.context.value['speckle_type'] == "Speckle.Core.Models.DataChunk")
                _ = m.context.value.pop(k)
                m.context.value[k] = encoder(_) # is this ok? channging while iterating
        if k == 'matrix':
            _ = m.context.value[k]
            assert(isinstance(_, list))
            assert(all(isinstance(i, (int, float)) for i in _))
            # need this? too restrictive?                        'other' seems meaningless and subject to change.
            # assert(m.context.value['speckle_type'] == "Objects.Other.Transform") 
            _ = m.context.value.pop(k)
            m.context.value[k] = encoder(_) # is this ok? channging while iterating
    return d


def data_encode(d: list) -> str:
    from numpy import savez_compressed as save, array
    #from numpy import save
    _ = d
    _ = array(d, dtype='float16')
    from io import BytesIO
    def sv(d):
        _ = BytesIO()
        #save(_, d)
        save(_, array=d)
        return _
    _ = sv(_)
    _.seek(0)
    _ = _.read()
    from base64 import b64encode
    _ = b64encode(_)
    _ = _.decode()
    return _


def data_decode(d: str) -> 'array':
    _ = d
    from base64 import b64decode
    _ = b64decode(_,)
    from numpy import load
    from io import BytesIO
    _ = BytesIO(_)
    _ = load(_)
    _ = _['array']
    return _


# can take json or speckleid
def rdf(d, data_lists=False):  #TODO: propagate "engine" option to encode data list
    _ = d
    _ = remove_at(_)
    _ = url_quote(_)
    if data_lists:
        _ = encode_data_lists(_, encoder=data_encode)
    else: # "erase" the data
        _ = encode_data_lists(_, encoder=lambda l: "")
    # the num lists wont show
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
    _ = dumps(_) # TODO: how to say base64 encoded?
    _ = Graph().parse(data=_, format='json-ld')
    from io import BytesIO
    o = BytesIO()
    _ = _.serialize(o, 'text/turtle')
    o.seek(0)
    _ = o
    return _


if __name__ == '__main__':

    def write_json(stream_id, object_id, path='data.json', safe=True):
        # for debugging
        from speckle.graphql import queries, query
        _ = queries()
        _ = _.objects(stream_id, object_id)
        _ = query(_) # dict
        if not safe:
            _ = remove_at(_)
            _ = url_quote(_)
            _ = encode_data_lists(_)
        from json import dump
        from pathlib import Path
        dump(_, open(Path(path), 'w'),)
    
    import fire
    fire.Fire(write_json)

