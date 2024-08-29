
def get_json(stream_id, object_id):
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.objects(stream_id, object_id)
    _ = query(_) # dict
    return _ 
