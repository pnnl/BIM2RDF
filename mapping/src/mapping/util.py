

from pathlib import Path
from typing import Callable
from .engine import Triples
ttl = str
from io import BytesIO
def get_data(src: BytesIO | ttl | Path | Callable[[], ttl ]  ) -> Triples:
    from pyoxigraph import Store
    if isinstance(src, BytesIO):
        s = Store()
        s.bulk_load(src, 'text/turtle')
        _ = Triples(q.triple for q in s)
        return _
    elif isinstance(src, ttl):
        _ = src.encode()
        _ = BytesIO(_)
        _ = get_data(_)
        return _
    elif isinstance(src, Path):
        assert(src.suffix == '.ttl')
        _ = open(src, 'rb')
        _ = _.read()
        _ = BytesIO(_)
        _ = get_data(_)
        return _
    elif callable(src):
        _ = src()
        _ = get_data(_)
        return _
    else:
        raise ValueError('dont know how to get data')

def filter_mapped():
    # so then these could just be used for the inferencing
    _ = """
    construct {?s ?p ?o }
    where {
    ?s ?p ?o.
    <<?s ?p ?o>> <http://meta> <<?ms <http://mmeta/query> ?mo>> .
    #FILTER(
    #    regex(str(?p), "data.ashrae.org/standard223" ) 
    # || regex(str(?o), "data.ashrae.org/standard223" )
    # || regex(str(?p), "www.w3.org/2000/01/rdf-schema" ) 
    # || regex(str(?o), "www.w3.org/2000/01/rdf-schema" )
    # || regex(str(?p), "www.w3.org/1999/02/22-rdf-syntax-ns" )
    # || regex(str(?o), "www.w3.org/1999/02/22-rdf-syntax-ns" )
    #)
    }
    """
    return _





