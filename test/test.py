from pathlib import Path
import pytest
    

#@pytest.fixture
from functools import cache
@cache
def params():
    _ = Path('params.yaml')
    _ = _.read_text()
    from yaml import safe_load
    _ = safe_load(_)
    return _

#@pytest.fixture
#def db():#(params)
#from subprocess import check_call
#check_call('bim2rdf -p params.yaml')


def is_eq(g1: str, g2: str):
    from rdflib import Graph
    g1: Graph = Graph().parse(data=g1, format='text/turtle') if isinstance(g1, str) else g1
    g2: Graph = Graph().parse(data=g2, format='text/turtle') if isinstance(g2, str) else g2
    from rdflib.compare import isomorphic
    return isomorphic(g1, g2)


from bim2rdf.queries import queries
@pytest.fixture(params=list(n for n in queries if n not in {'ontology'}))
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

