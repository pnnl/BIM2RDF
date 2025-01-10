from requests.auth import AuthBase

class TokenAuth(AuthBase):
    def __init__(self,):
        from .config import token
        self.token = token
        self.auth_scheme = 'Bearer'
        
    def __call__(self, request):
        request.headers['Authorization'] = f'{self.auth_scheme} {self.token}'
        return request

def get_session( ):
    from requests import Session
    return Session()
