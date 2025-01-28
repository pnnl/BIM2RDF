
from .config import server
gql_url = f'https://{server}/graphql'


def client():
    from gql import Client
    from .requests import TokenAuth
    from gql.transport.requests import RequestsHTTPTransport
    default_transport = RequestsHTTPTransport(url=gql_url, auth=TokenAuth())
    _ = Client(transport = default_transport, fetch_schema_from_transport=True)
    return _


def get_schema(client=client):
    from gql import gql
    #transport.session = requests_cache.CachedSession('http_cache')
    #from requests import Session
    #_.session = Session()
    _ = client()
    _.execute(gql('{_}')) # some kind of 'nothing' query just to initialize things
    _ = _.schema
    return _


import gql.dsl as dsl

def get_dsl_schema(client=client) -> dsl.DSLSchema:
    _ = get_schema(client=client)
    _ = dsl.DSLSchema(_)
    return _


def get_void_query(client=client):
    _ = get_dsl_schema(client=client)
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
    _ = client()
    _ = _.execute(q)
    return _

class queries:

    biglim = 999999 # https://github.com/specklesystems/speckle-server/issues/3908
    def __init__(self, client=client):
        from types import SimpleNamespace as NS
        _q = """
        {
        apps {
            id
        }
        }
        """
        from .graphql import get_dsl_schema
        self.schema = get_dsl_schema(client=client)
    
    # dev the query at https://app.speckle.systems/graphql
    def general_meta(self):
        return """ query  { activeUser {
        projects { items {
            id
            name
            models { items {
                id
                name
                createdAt
                versions { items {
                    id
                    referencedObject
                    createdAt
        }}}}}}}}
        """
    
    def objects(self, *, project_id, object_id):
        _ = """ query {
        project(id: "project_id") {
            object(id: "object_id") {
            data
            children(limit: biglim, depth: biglim) {
                objects {
                data
        }}}}}
        """
        _ = _.replace('project_id', project_id)
        _ = _.replace('object_id',  object_id)
        _ = _.replace('biglim', str(self.biglim))
        return _

queries = queries()