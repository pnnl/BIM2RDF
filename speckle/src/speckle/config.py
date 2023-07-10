
def config():
    from speckle.server import apikey, test, contextualize, rdf
    contextualize()
    rdf()
    test()
    apikey()
    from speckle.requests import TokenAuth, get_cached_session
    TokenAuth()
    get_cached_session()
    from speckle.meta import contextualize, rdf
    contextualize()
    rdf()
    from speckle.objects import find_list_fields, sample_json, remove_at,url_quote,rdf
    find_list_fields()
    sample_json()
    remove_at()
    url_quote()
    rdf()
    from speckle.graphql import CachedRequestHTTPTransport, client, get_schema, get_dsl_schema, get_void_query,query,queries
    CachedRequestHTTPTransport()
    client()
    get_schema()
    get_dsl_schema()
    get_cached_session()
    query()
    queries() 
    
if __name__ == '__main__':
    config()