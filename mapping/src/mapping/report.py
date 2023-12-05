
class Report:
    def __init__(self, store):
        self.store = store

    def validation(self):
        from mapping.utils.queries import queries
        from mapping.utils.tables import query_table
        _ = self.store.query(queries.shacl_report)
        _ = query_table(_)
        return _




