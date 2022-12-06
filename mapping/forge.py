import requests

def get_credentials():
    import yaml
    from pathlib import Path
    _ = yaml.safe_load( (Path(__file__) / '..' / 'secret.yaml').read_bytes())
    from types import SimpleNamespace as NS
    return NS(id=_['id'], secret=_['secret'])

    

def get_token():
    _ = get_credentials()
    import requests
    _ = requests.post(
            'https://developer.api.autodesk.com/authentication/v2/token',
            auth=(_.id, _.secret),
            params={
                'grant_type':'client_credentials',
                'scope': 'data:read'},
            )
    return _
