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

def object():
    _ = transport()#.objects
    from specklepy.api import operations
    from specklepy.transports.memory import MemoryTransport # for caching
    _ = operations.receive(obj_id='32c394baf2edf75a3fdd3fe2a14e7c59', remote_transport=_, local_transport=MemoryTransport())
    return _
    # graphql that doest recompose
    #_ = client().object.get(stream_id='4256f155c0', object_id='32c394baf2edf75a3fdd3fe2a14e7c59')
    return _


def json():
    from specklepy.serialization.base_object_serializer import BaseObjectSerializer
    _ = BaseObjectSerializer()
    _ = _.write_json(object(),)
    return _


def write():
    _ = json()
    _ = _[1] # the json
    open('neaa.speckle.json', 'w').write(_)


