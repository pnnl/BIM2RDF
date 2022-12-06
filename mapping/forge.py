import requests

def get_app_credentials():
    import yaml
    from pathlib import Path
    _ = yaml.safe_load( (Path(__file__) / '..' / 'secret.yaml').read_bytes())
    from types import SimpleNamespace as NS
    return NS(id=_['id'], secret=_['secret'])


import requests
import json

from functools import lru_cache as cache


@cache  # timeout would be nice
def get_token():
    _ = get_app_credentials()
    _ = requests.post(
            'https://developer.api.autodesk.com/authentication/v2/token',
            auth=(_.id, _.secret),
            params={
                'grant_type':'client_credentials',
                'scope': 'data:read'},
            )
    import json
    _ = json.loads(_.content)
    _ = _['access_token']
    return _


import requests.auth
class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


@cache
def get_hub(): # this shows up in bim360 url but have to add 'b.'+id
    _ = requests.get(
        'https://developer.api.autodesk.com/project/v1/hubs',
        auth=BearerAuth(get_token()),)
    _ = _.content
    _ = json.loads(_)
    return _

@cache
def get_projects(): # again shows up in the project url but has to add 'b.'+id
    _ = get_hub()
    _ = _['data'][0]['id']
    _ = requests.get(
        f'https://developer.api.autodesk.com/project/v1/hubs/{_}/projects',
        auth=BearerAuth(get_token()),)
    _ = _.content
    _ = json.loads(_)
    return _


@cache
def proto_medoffice():
    _ =  get_projects()['data'][0]
    assert(kw in _['name'].lower() for kw in {'med', 'office'})
    return _['id']


projects = {'proto-medoffice': proto_medoffice }


@cache
def get_folders(project):
    _ = get_hub()
    _ = _['data'][0]['id']
    _ = requests.get(
        f'https://developer.api.autodesk.com/project/v1/hubs/{_}/projects/{project()}/topFolders',
        auth=BearerAuth(get_token()),)
    _ = _.content
    _ = json.loads(_)
    return _


proto_medoffice_id = "urn:adsk.wipprod:fs.file:vf.neWKg6LWQWWe0HVbGQ3QZg"#?version=1"
proto_medoffice_id = "urn%3Aadsk.wipprod%3Adm.lineage%3AneWKg6LWQWWe0HVbGQ3QZg".replace('%3A', ':')
proto_medoffice_folder = 'urn:adsk.wipprod:fs.folder:co.zj-rVepdRg60MgKWe3DKsQ'

@cache
def get_folder_contents(project, folder):
    _ = requests.get(
        f'https://developer.api.autodesk.com/data/v1/projects/{project()}/folders/{folder()}/contents',
        auth=BearerAuth(get_token()),)
    _ = _.content
    _ = json.loads(_)
    return _


@cache
def get_exchange(data_exchange_id):
    _ = requests.get(
        f'https://developer.api.autodesk.com/exchange/v1/exchanges',
        auth=BearerAuth(get_token()),
        params={'filters':f"attribute.exchangeFileUrn=={data_exchange_id}" },
        )
    _ = _.content
    _ = json.loads(_)
    return _


def test():
    f = lambda: proto_medoffice_folder
    p = projects['proto-medoffice']
    _ = get_folder_contents(p, f)
    return _
