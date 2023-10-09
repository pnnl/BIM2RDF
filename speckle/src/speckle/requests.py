from requests.auth import AuthBase

class TokenAuth(AuthBase):
    def __init__(self,):
        from .server import apikey
        self.token = apikey()
        self.auth_scheme = 'Bearer'
        
    def __call__(self, request):
        request.headers['Authorization'] = f'{self.auth_scheme} {self.token}'
        return request


# global install
#requests_cache.install_cache('http_cache', allowable_methods={'GET', 'HEAD', 'POST'})
def get_session(cached = False, ):
    if cached:
        from project import root
        db_file = root / 'speckle' /'http_cache'
        db_file = str(db_file)
        import requests_cache
        _ = requests_cache.CachedSession(
                cache_name=db_file,
                allowable_methods={'GET', 'HEAD', 'POST'},
                # expire_after
                )
        return _
    else:
        from requests import Session
        return Session()
