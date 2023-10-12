
class Report:
    def __init__(self, store):
        self.store = store

    def validation(self):
        from .utils.queries import queries
        _ = queries.shacl
        return _
        

