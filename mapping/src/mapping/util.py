

from pathlib import Path
from typing import Callable
from .engine import Triples
ttl = str
from io import BytesIO
def get_data(src: BytesIO | ttl | Path | Triples | Callable[[], ttl ]  ) -> Triples:
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
    elif isinstance(src, Triples):
        return src
    elif callable(src):
        _ = src()
        _ = get_data(_)
        return _
    else:
        raise ValueError('dont know how to get data')
    
parts = {
    's223': "standard223",
    'rdfs': "rdf-schema",
    'rdf': '22-rdf-syntax-ns',
    'qudt': 'qudt',
    'shacl': 'shacl',
    }


def make_regex_parts(parts):
    for part in parts:
        for po in ('p', 'o'):
            #       uri cast as string so that regex can be applied
            yield f"""regex(str(?{po}), "{part}")"""


mapped_pattern = "<<?s ?p ?o>> <http://meta> <<?ms <http://mmeta/query> ?mo>> ."
# need to use filter
full_ontology_pattern = '<<?s ?p ?o>> <http://meta> <<<http://mmeta/python#function> <http://mmeta/python#name> "get_ontology">> .'

def filter_mapped():
    # so then these could just be used for the inferencing
    _ = f"""
    construct {{?s ?p ?o }}
    where {{
    ?s ?p ?o.
    # since all data went through a query to be mapped, this applies.
    # but check if still applies when queries are used for something else.
    {mapped_pattern}
    }}
    """
    # or can filter out
    # <http://meta> <<<http://mmeta/python#function> <http://mmeta/python#name> "overlap">> .
    return _



def filter_ontology():
    # query to get data belonging to the ontology
    _ = f"""
    construct {{?s ?p ?o }}
    where {{
    ?s ?p ?o.
    {{{full_ontology_pattern}}}
    union
    {{{mapped_pattern}}}
    }}
    """
    # or could say NOT speckle.
    # or filter FOR the 
    # FILTER({ ' || '.join(make_regex_parts(parts.values())) } )
    return _


def batched(iterable, n):
    # this is a built in in python 3.12
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    from itertools import islice
    while batch := tuple(islice(it, n)):
        yield batch


def split_triples(triples, chunk_size=1000, odir='out'):
    from pathlib import Path
    odir = Path(odir)
    if not odir.exists() or odir.is_file():
        odir.mkdir()
    from pyoxigraph import serialize
    for i, chunk in enumerate(batched(get_data(triples), chunk_size)):
        serialize(
            chunk,
            f"{odir}/{i}.ttl",
            'text/turtle')


def sort_triples(triples):
    _ = get_data(triples)
    _ = sorted(_, key=lambda t: str(t) )
    return Triples(_)


def combine_ttls(dir: Path, out=Path('out.ttl')):
        dir = Path(dir)
        from pyoxigraph import Store
        s = Store()
        for f in dir.glob('*.ttl'):
            s.bulk_load(str(f), 'text/turtle')
        s.dump(str(out), 'text/turtle')
        return out


if __name__ == '__main__':
    from fire import Fire
    Fire(combine_ttls)
