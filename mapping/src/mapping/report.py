
class Report:
    def __init__(self, store):
        self.store = store

    def validation(self):
        from mapping.utils.queries import queries
        from mapping.utils.tables import query_table
        _ = query_table(self.store, queries.shacl_report )
        return _


        

