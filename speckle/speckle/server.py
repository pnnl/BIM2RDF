
    


def apikey():
    import json
    from pathlib import Path
    _ = open(Path(__file__) / '..' / '..'  /'secret.json')
    _  = json.load(_)
    _ = _['speckl_token']
    return _

from functools import lru_cache as cache

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
