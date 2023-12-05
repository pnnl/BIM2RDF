
class Report:
    def __init__(self, store):
        self.store = store

    def validation(self, filter=True):
        from mapping.utils.queries import queries
        from mapping.utils.tables import query_table
        _ = self.store.query(queries.shacl_report)
        _ = query_table(_)
        if filter:
            for q in {
                queries.rules.mapped,
                queries.rules.rdfs_inferred,
                queries.rules.shacl_inferred}:
                md = self.store.query(q)
                md = tuple(md)
                from itertools import chain
                md = chain((t[0] for t in md), (t[2] for t in md))
                md = (_.value for _ in md)
                md = frozenset(md)
                _ = _[_['focusNode'].isin(md)]
        return _

