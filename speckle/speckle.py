from functools import lru_cache as cache


def apikey():
    import json
    from pathlib import Path
    _ = open(Path(__file__) / '..' / 'secret.json')
    _  = json.load(_)
    _ = _['speckl_token']
    return _

@cache
def client():
    from specklepy.api.client import SpeckleClient
    from specklepy.api.credentials import get_account_from_token
    _ = apikey()
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
            




def server_transport(stream_id):
    from specklepy.transports.server import ServerTransport
    return ServerTransport(stream_id=stream_id, client=client())

def sqlite_transport(fn='cache'):
    from specklepy.transports.sqlite import SQLiteTransport
    return SQLiteTransport(fn)


from requests.auth import AuthBase
class TokenAuth(AuthBase):
    def __init__(self,):
        self.token = apikey()
        self.auth_scheme = 'Bearer'
    def __call__(self, request):
        request.headers['Authorization'] = f'{self.auth_scheme} {self.token}'
        return request



def get_json(stream_id, object_id):
    import yaml
    from pathlib import Path
    _ = open(Path(__file__) / '..' / 'secret.yaml')
    _  = yaml.safe_load(_)
    _ = _['speckl_token']
    
    import requests
    server = 'http://speckle.xyz'
    _ = requests.get(f"{server}/objects/{stream_id}/{object_id}", auth=TokenAuth(_))
    _ = _.json()
    return _


def get(stream_id, object_id):
    from specklepy.api import operations
    return operations.receive(
            object_id,
            remote_transport=server_transport(stream_id),
            local_transport=sqlite_transport())


def json(w=False): # (stream_id, object_id):
    # via speckle api
    from specklepy.serialization.base_object_serializer import BaseObjectSerializer
    serializer = BaseObjectSerializer()
    _ = app_info()
    # i = next(_) # test
    # got = None
    # for i in (_):
    #     if i.stream.id == '316586b660':
    #         got = True
    #         break
    # if not got: raise ValueError('streamid not found')
    #_ = get(i.stream.id, i.commit.referencedObject)
    _ = get('316586b660', '37c11d7537a358eb35970e09b3837aa8') # this id is nowhere to be found in the json
    #return i, _
    # https://github.com/specklesystems/specklepy/issues/237#issuecomment-1382598762
    id, j = serializer.write_json(_)  # creating a new id for some reason.
    open(f"{id}.json", 'w').write(j)
    from json import loads
    return loads(j)


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


def id_field(d: dict) -> dict:
    """creates speckle identifiers"""
    # i think i had to do this outside of @context
    #https://stackoverflow.com/questions/67444075/json-ld-assign-custom-uris-to-blank-nodes-within-context
    #base_uri = lambda: 
    d = d.copy()
    for m in parsing.ids.find(d):
        k = str(m.path)
        _ = m.context.value.pop(k)
        m.context.value[f"@{k}"] = f"{base_uri()}{_}" # TODO: do i really need to do this here?
    return d


def id_ref(d: dict) -> dict:
    """creates links to ids"""
    d = d.copy()
    for m in parsing.id_refs.find(d):
        m.context.value['referencedId'] = f"{base_uri()}{m.value}"
        m.context.value.pop('speckle_type')
    return d

def id_(d: dict) -> dict:
    _ = d
    _ = id_field(_)
    _ = id_ref(_)
    return _

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
    #from pyld.jsonld import KEYWORDS
    # take out the @
    #KEYWORDS = {k[1:] for k in KEYWORDS}
    # maybe_bad = {f for f in _ if f in KEYWORDS}
    # maybe_bad = {'direction', 'id', 'type', 'value'} # id,type, value, match jsonld interpretation
    maybe_bad = {'id'}
    from urllib.parse import quote
    # creating the 'speckle ontology'
    #d['@context'] = {f:f"{base_uri()}{quote(f)}" for f in _ if f not in maybe_bad }  # or just use @vocab?
    context = {'@vocab': base_uri(), }#'referencedId': {'@type': '@id'} }
    context = {'@vocab': base_uri(), 'referencedId': {'@type': '@id'} }
    context = {'@vocab': base_uri(), 'referencedId': '@id' }
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



def rdf():
    # now just map? can make bnode a subject?
    _ = {
            'id':'o1', # ok maybe just take this id as speckle and reinterpret as schema.org/id
            'Outside': 'sdf',
            'inside': [
                {'id': 'i1', 
                'p': 3},
                {'id': 'i2', 
                'p': 4}
            ]
        }
    _ = sample_json()
    _ = remove_at(_)
    _ = id_(_)
    _ = contextualize(_)
    from pyld import jsonld as lj
    _ = lj.flatten(_, )#contextualize({})['@context']) 
    _ = lj.to_rdf(_, options=NS(format='application/n-quads').__dict__ ) #close to flatten
    return _



# global install
#requests_cache.install_cache('http_cache', allowable_methods={'GET', 'HEAD', 'POST'})
def get_cached_session():
    from pathlib import Path
    db_file = Path(__file__)/'..'/'http_cache'
    db_file = str(db_file)
    import requests_cache
    _ = requests_cache.CachedSession(
                cache_name=db_file,
                allowable_methods={'GET', 'HEAD', 'POST'}) # default transport method is post
    return _


from gql.transport.requests import RequestsHTTPTransport
from requests.adapters import HTTPAdapter, Retry
from gql.transport.exceptions import TransportAlreadyConnected


class CachedRequestHTTPTransport(RequestsHTTPTransport):

    def connect(self):
        #https://github.com/graphql-python/gql/issues/387#issuecomment-1435323862
        # copypaste
        if self.session is None:
            # Creating a session that can later be re-use to configure custom mechanisms
            self.session = get_cached_session()
            # If we specified some retries, we provide a predefined retry-logic
            if self.retries > 0:
                adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=self.retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=None,
                    )
                )
                for prefix in "http://", "https://":
                    self.session.mount(prefix, adapter)
        else:
            raise TransportAlreadyConnected("Transport is already connected")

    def xconnect(self):
        # not annoying version
        if self.session is None:
            self.session = requests_cache.CachedSession('http_cache')

gql_url = 'https://speckle.xyz/graphql'


import gql.dsl as dsl



def client():
    from gql import Client
    transport=CachedRequestHTTPTransport(url=gql_url, auth=TokenAuth() )
    _ = Client(
        transport=transport,
        fetch_schema_from_transport=True)
    return _


def get_schema():
    from gql import gql
    #transport.session = requests_cache.CachedSession('http_cache')
    #from requests import Session
    #_.session = Session()
    _ = client()
    _.execute(gql('{_}')) # some kind of 'nothing' query just to initialize things
    _ = _.schema
    return _
    from graphql import print_schema
    _ = print_schema(_)
    return _

def get_dsl_schema() -> dsl.DSLSchema:
    _ = get_schema()
    _ = dsl.DSLSchema(_)
    return _


def test():
    #ds = get_dsl_schema()
    #_ = ds.Query.apps.select()
    q = """
    {
    apps {
        id
    }
    }
    """
    _ = client()
    from gql import gql
    _ = _.execute(gql(q))
    return _




if __name__ == '__main__':
    test()
    #_ = rdf()
    #from rdflib import Graph
    #_ = Graph().parse(data=_, format='nquads')
    #_.bind('spkl', base_uri())
    #_.serialize('speckle.ttl', format='ttl')



    

