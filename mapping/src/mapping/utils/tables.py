
def query_table(query_result): # TODO: put in docs?
    _ = query_result
    import pandas as pd
    if hasattr(_, 'variables'):
        columns = [v.value for v in _.variables]
    else:
        # ie is a construct query
        columns = ['subject', 'predicate', 'object']
    _ = pd.DataFrame(
            tuple( #                                  nested triple
                tuple( (c.value if hasattr(c, 'value') else str(c))
                    for c in qs)
                for qs in _),
            columns=columns)
    return _