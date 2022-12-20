from functools import lru_cache as cache

@cache
def client():
    from specklepy.api.client import SpeckleClient
    from specklepy.api.credentials import get_account_from_token
    import yaml
    from pathlib import Path
    _ = open(Path(__file__) / '..' / 'secret.yaml')
    _  = yaml.safe_load(_)
    _ = _['speckl_token']
    account = get_account_from_token(_, 'http://speckle.xyz')
    assert(account)

    client = SpeckleClient() # or whatever your host is
    # client = SpeckleClient(host="localhost:3000", use_ssl=False) or use local server
    client.authenticate_with_account(account)
    return client  # gets 'resources' like streams, objs




def app_info(client=client(), ):
    from types import SimpleNamespace as NS
    streams = (s for s in client.stream.list() )
    def _(streams=streams):
        for s in streams:
            yield from ( (s,b) for b in client.branch.list(s.id, 99, 99))
    def commits(streams=streams):
        for s in streams:
            yield from c.commit.list(s.id)
    for s,b in _():
        for c in b.commits.items:
            yield NS(stream=s,branch=b,commit=c)
    #yield from _() # _[1].commits.items
    #from itertools import product
    #yield from product(streams, branches())            
            

from specklepy.serialization.base_object_serializer import BaseObjectSerializer
serializer = BaseObjectSerializer()


from specklepy.transports.sqlite import SQLiteTransport
from specklepy.transports.server import ServerTransport
from specklepy.api import operations


def server_transport(stream_id):
    return ServerTransport(stream_id=stream_id, client=client())

def sqlite_transport(fn='cache'):
    return SQLiteTransport(fn)


def get(stream_id, object_id): 
    return operations.receive(
            object_id,
            remote_transport=server_transport(stream_id),
            local_transport=sqlite_transport())

    


def json(w=False): # (stream_id, object_id)
    _ = app_info()
    i = next(_) # test
    _ = get(i.stream.id, i.commit.referencedObject)
    id, j = serializer.write_json(_)
    open(f"{id}.json", 'w').write(j)
    from json import loads
    return loads(j)


import jsonpath_ng as jp
from types import SimpleNamespace as NS
parsing = NS(
    fields = jp.parse("$..*"),     # recursive
    ids = jp.parse("$..id"),       # useful for extracting out objs...
    # ...relations could be extracted b/c match results are nested DatumInContext.context -> DatumInContext
    jsonld = NS(**{k: jp.parse(f"$..{k}") for k in {'id', 'type', 'value'}}) # there's also speckle_type
)


def sample_json():
    _ = open('051cd6318fc716ff55ce452121ed59ee.json').read()
    import json
    _ = json.loads(_)
    return _

def remove_at(d: dict) -> dict:
    # need copy? functional programming rules
    d = d.copy()
    # can't have @. collides with jsonld.
    for m in parsing.fields.find(d):
        k = str(m.path)
        if k.startswith('@'):
            _ = m.context.value.pop(k)
            m.context.value[k[1:]] = _ # is this ok? channging while iterating
    return d


# def adapt(d: dict) -> dict: i think this goes into @graph?
#     # by adding @
#     d = d.copy()
#     from itertools import chain
#     for m in chain.from_iterable(map(lambda _:_.find(d), (parsing.jsonld.__dict__.values()))):
#         k = str(m.path)
#         _ = m.context.value.pop(k)
#         m.context.value[f"@{k}"] = _
#     return d


base_uri = lambda: 'http://speckle.systems/'

def contextualize(d: dict) -> dict:
    # jsonld context
    d = d.copy()
    _ = {str(m.path) for m in parsing.fields.find(d)}
    # generic
    from pyld.jsonld import KEYWORDS
    # take out the @
    KEYWORDS = {k[1:] for k in KEYWORDS}
    maybe_bad = {f for f in _ if f in KEYWORDS} # Out[26]: {'direction', 'id', 'type', 'value'} # id,type, value, match jsonld
    from urllib.parse import quote
    d['@context'] = {f:f"{base_uri()}{quote(f)}" for f in _ if f not in maybe_bad }
    # speckle specific
    return d


def test():
    _ = sample_json()
    _ = {'Networks': 'sdf', 'id':'sdffds'}
    _ = remove_at(_)
    #_ = adapt(_)
    _ = contextualize(_)
    #return _
    from pyld import jsonld as lj
    #_ = lj.to_rdf(_) close to flatten
    #_ = lj.expand(_, )# NS(graph=True).__dict__ )
    #_ = lj.flatten(_, contextualize({})['@context']  ) # creates @graph
    return _


