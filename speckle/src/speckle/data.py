
def get_json(project_id, object_id):
    from speckle.graphql import queries, query
    _ = queries()
    _ = _.objects(project_id, object_id)
    _ = query(_) # dict
    return _ 
