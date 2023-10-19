

gql_url = 'https://speckle.xyz/graphql'


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
    from graphql import print_schema
    _ = print_schema(_)
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


biglim = 99999


# could make it a class.
# Queries
# def query1
# def execute
def queries(client=client):
    from types import SimpleNamespace as NS
    _q = """
    {
    apps {
        id
    }
    }
    """
    from .graphql import get_dsl_schema
    s = get_dsl_schema(client=client)
    
    def general_meta():
        return s.Query.streams.args(limit=biglim).select(
            s.StreamCollection.items.select(
                s.Stream.id,
                s.Stream.name,
                s.Stream.branches.select(
                    s.BranchCollection.items.select(
                        s.Branch.id,
                        s.Branch.name,
                        s.Branch.createdAt,
                        s.Branch.commits.select(
                            s.CommitCollection.items.select(
                                s.Commit.id,
                                s.Commit.referencedObject,
                                s.Commit.createdAt
                                )
                            )
                        )
                )  )  )
    
    # stick with the rest api b/c this add a lil more nesting?
    def objects(stream_id, object_id):
        return s.Query.stream.args(id=stream_id).select(
                    s.Stream.id,
                    s.Stream.object.args(id=object_id).select(
                        s.Object.data,
                        s.Object.children.args(limit=biglim, depth=biglim).select(
                            s.ObjectCollection.totalCount,
                            s.ObjectCollection.objects.select(
                                s.Object.data,
                            )
                        )))
    
    return NS(general_meta=general_meta, objects=objects)


