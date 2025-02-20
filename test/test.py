from pathlib import Path
import pytest
    

#@pytest.fixture
def params():
    _ = Path('params.yaml')
    _ = _.read_text()
    from yaml import safe_load
    _ = safe_load(_)
    return _


from rdflib import Graph
def is_eq(g1: Graph|str, g2: Graph|str):
    from rdflib import Graph
    g1 = Graph().parse(data=g1, format='text/turtle') if isinstance(g1, str) else g1
    g2 = Graph().parse(data=g2, format='text/turtle') if isinstance(g2, str) else g2
    from rdflib.compare import isomorphic
    return isomorphic(g1, g2)



from bim2rdf.queries import queries
@pytest.fixture(params=list(n for n in queries.names if n not in {'ontology'}))
def query(request):
    return request.param
    #_ = getattr(queries, request.param)
    #return _

def test_ttl(query, file_regression):
    p = params()
    from bim2rdf.queries import query as queryf
    ttl = queryf(
        db=Path(p['db_dir']),
        query=query,
        out=None)
    def check_fn(obtained_fn, expected_fn):
        o, e = map(lambda f: open(f).read(), (obtained_fn, expected_fn))
        if not is_eq(o, e): raise AssertionError
    file_regression.check(ttl, check_fn=check_fn, extension='.ttl')

