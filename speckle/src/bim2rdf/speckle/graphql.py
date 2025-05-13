from bim2rdf.core.config import config
gql_url = f'https://{config.speckle.server}/graphql'
del config

def client():
    from gql import Client
    from .requests import TokenAuth
    from gql.transport.requests import RequestsHTTPTransport
    default_transport = RequestsHTTPTransport(url=gql_url, auth=TokenAuth())
    #from gql.transport.aiohttp import AIOHTTPTransport
    #default_transport = AIOHTTPTransport(url=gql_url,headers= {'Authorization': TokenAuth().token}  )
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


def query_function(q=get_void_query(), client=client) -> dict: # json
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
from bim2rdf.cache import cache
@cache
def query(*p, **k): return query_function(*p, **k)

class queries:

    def __init__(self, client=client):
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
    
    biglim = 999999 # https://github.com/specklesystems/speckle-server/issues/3908
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


if __name__ == '__main__':
    from fire import Fire
    from pathlib import Path
    def _(q: str | Path,):
        """query"""
        if isinstance(q, str):
            if Path(q).exists():
                q = Path(q).read_text()
        return query(q)
    Fire({'query': _, 'queries': queries})
