def config():
    #from speckle.requests import TokenAuth #get_cached_session TokenAuth
    #TokenAuth()
    from speckle.server import (
        apikey, test, contextualize, rdf
    )
    contextualize()
    rdf()
    test()
    apikey()

    from .requests import TokenAuth, get_cached_session
    TokenAuth()
    get_cached_session()
    from .meta import 

   

    #get_cached_session()
    

if __name__ == '__main__':
    config()