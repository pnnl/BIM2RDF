from pyoxigraph import Store
def og2rg(og: Store,) -> Graph:
    from io import BytesIO
    _ = BytesIO()
    to = 'text/turtle'
    og.dump(_, to)
    _.seek(0)
    _ = Graph().parse(_, to)
    return _