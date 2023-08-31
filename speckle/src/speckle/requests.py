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
# TODO expire this somehow
def get_session(dev = True):
    from project import root
    db_file = root / 'speckle' /'http_cache'
    db_file = str(db_file)
    import requests_cache
    from requests_cache import DO_NOT_CACHE,EXPIRE_IMMEDIATELY
    if dev:
        _ = requests_cache.CachedSession(
                cache_name=db_file,
                allowable_methods={'GET', 'HEAD', 'POST'},
                expire_after=DO_NOT_CACHE) # default transport method is post
        return _
    else:
        exp_session = requests_cache.CachedSession(
            cache_name=db_file,
            allowable_methods={'GET', 'HEAD', 'POST'},
            expire_after= EXPIRE_IMMEDIATELY)
        return exp_session
