from gql.transport.requests import RequestsHTTPTransport
from requests.adapters import HTTPAdapter, Retry
from gql.transport.exceptions import TransportAlreadyConnected


class CachedRequestHTTPTransport(RequestsHTTPTransport):

    def connect(self):
        #https://github.com/graphql-python/gql/issues/387#issuecomment-1435323862
        # copypaste
        if self.session is None:
            from .requests import get_cached_session
            # Creating a session that can later be re-use to configure custom mechanisms
            self.session = get_cached_session()
            # If we specified some retries, we provide a predefined retry-logic
            if self.retries > 0:
                adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=self.retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504],
                        allowed_methods=None,
                    )
                )
                for prefix in "http://", "https://":
                    self.session.mount(prefix, adapter)
        else:
            raise TransportAlreadyConnected("Transport is already connected")

    def xconnect(self):
        # not annoying version
        if self.session is None:
            self.session = requests_cache.CachedSession('http_cache')

gql_url = 'https://speckle.xyz/graphql'


def client():
    from gql import Client
    from .requests import TokenAuth
    transport=CachedRequestHTTPTransport(url=gql_url, auth=TokenAuth() )
    _ = Client(
        transport=transport,
        fetch_schema_from_transport=True)
    return _



def get_schema():
    from gql import gql
    #transport.session = requests_cache.CachedSession('http_cache')
    #from requests import Session
    #_.session = Session()
    _ = client()
    _.execute(gql('{_}')) # some kind of 'nothing' query just to initialize things
    _ = _.schema
    return _
    from graphql import print_schema
    _ = print_schema(_)
    return _

import gql.dsl as dsl

def get_dsl_schema() -> dsl.DSLSchema:
    _ = get_schema()
    _ = dsl.DSLSchema(_)
    return _


def get_void_query():
    _ = get_dsl_schema()
    _ = _.Query._
    return _


def query(q=get_void_query(), client=client) -> dict: # json
    if isinstance(q, str):
        from gql import gql
        q = gql(q)
    elif isinstance(q, dsl.DSLField):#DSLSchema):?
        from gql.dsl import dsl_gql, DSLQuery
        q = DSLQuery(q)
        q = dsl_gql(q)
    else:
        raise TypeError('not a query')
    #  #https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html#precedence
    # somehow control cache expiry w/ timely queries TODO
    _ = client()
    _ = _.execute(q)
    return _


biglim = 99999


# could make it a class.
# Queries
# def query1
# def execute
def queries():
    from types import SimpleNamespace as NS
    _q = """
    {
    apps {
        id
    }
    }
    """
    from .graphql import get_dsl_schema
    s = get_dsl_schema()
    
    streams = s.Query.streams.args(limit=biglim).select(
            s.StreamCollection.items.select(
                s.Stream.id, s.Stream.name))
    
    # stick with the rest api b/c this add a lil more nesting?
    objects = s.Query.stream.args(id="316586b660").select(
            s.Stream.id,
            s.Stream.object.args(id="37c11d7537a358eb35970e09b3837aa8").select(
                s.Object.data,
                s.Object.children.args(limit=biglim, depth=biglim).select(
                    s.ObjectCollection.totalCount,
                    s.ObjectCollection.objects.select(
                          s.Object.data,
                     )
                )))
    
    return NS(streams=streams, objects=objects)


def test():
    _ = queries().streams
    _ = query(_)
    return _


