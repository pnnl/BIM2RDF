from functools import lru_cache as cache

@cache
def client():
    from specklepy.api.client import SpeckleClient
    from specklepy.api.credentials import get_account_from_token
    import yaml
    from pathlib import Path
    _  = yaml.safe_load(
            open(
                Path(__file__) / '..' / 'secret.yaml')
                )
    _ = _['speckl_token']
    account = get_account_from_token(_, 'http://speckle.xyz')
    assert(account)

    client = SpeckleClient() # or whatever your host is
    # client = SpeckleClient(host="localhost:3000", use_ssl=False) or use local server
    client.authenticate_with_account(account)
    return client


def transport():
    from specklepy.transports.server import ServerTransport
    _ = ServerTransport(client=client(), stream_id='4256f155c0')
    return _



def stream():
    _ =  client().stream.get(id='4256f155c0')
    return _

def objects(id='856e4768f86cf6b470f399699df6be03'):
    _ = transport()#.objects
    from specklepy.api import operations
    from specklepy.transports.memory import MemoryTransport # for caching
    _ = operations.receive(obj_id=id, remote_transport=_, local_transport=MemoryTransport())
    return _

def object(id):
    # graphql that doest recompose
    _ = client().object.get(stream_id='4256f155c0', object_id=id)
    return _


def json(d=False):
    from specklepy.serialization.base_object_serializer import BaseObjectSerializer
    _ = BaseObjectSerializer()
    if d:
        _ = _.traverse_base(objects())
    else:
        _ = _.write_json(objects(),)
    return _


def write():
    _ = json(1)
    _ = _[1] # the json
    #from json import dump
    #dump()
    #open('neaa.speckle.json', 'w')


def get_json():
    return open('neaa.speckle.json')


def qi():
    import pandas as pd
    _ = pd.read_csv('neaalights.csv')
    ids =  _['Id'].values
    j = get_json().read()
    lj = (len(j))
    found = []
    for i in ids:
        #_ = j.find('"elementId":"'+str(int(i))+'"')
        _ = j.find(str(int(i)))
        if _ != -1: found.append((i, j[_-30_000: _+100]  ))#  j[max(0,_-100):min(lj,_+100) ] ))
    return found

def ql():
    import pandas as pd
    j = get_json().read()
    from re import finditer
    return finditer('fixture', j.lower())
