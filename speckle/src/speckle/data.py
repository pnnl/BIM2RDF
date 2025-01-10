

def json(*, project_id, object_id):
    from speckle.graphql import queries, query
    _ = queries.objects(project_id, object_id)
    _ = query(_) # dict
    return _ 


def rdf(*, project_id, object_id):
    _ = json(project_id=project_id, object_id=object_id)
    from .meta import prefixes
    prefixes.meta, prefixes.concept
    from json2rdf import j2r
    _ = j2r(_) # TODO NOW the prefix stuff
    return _
