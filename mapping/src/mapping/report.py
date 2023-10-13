
class Report:
    def __init__(self, store):
        self.store = store

    def validation(self):
        from .utils.queries import queries
        #_ = queries.rules.shacl#_report
        _ = queries.shacl_report
        return _
        

