"""
distribution tasks
"""
from pathlib import Path

bdg2no = {
    'Pritoni': 0,
    'proto med-office': 1,
}

from graphdb.tasks import upload_graph


#out_selections: None | list =None, #'all'+{a for a in dir(queries.rules) if not ((a == 'q' ) or (a.startswith('_')) ) },
# if out_selections:
#         from pyoxigraph import Store, Quad
#         s = Store()
#         if isinstance(out_selections, str):
#             out_selections = (out_selections,)
#         else:
#             assert(isinstance(out_selections, (tuple, list, set, frozenset)) )

#         from .utils.queries import queries
#         for q in out_selections:
#             q = getattr(queries.rules, q)
#             q = _.query(q)
#             q = tuple(q) # why do i have to do this?!
#             if q: s.bulk_extend(Quad(*t) for t in q)
#             del q
#         _ = s; del s
# if not out:
#         return _
#     out = Path(out)
#     if split_out:
#         out = Path('/'.join((out).parts[:-1] + (out.stem,)))
#         if out.exists():
#             from shutil import rmtree
#             rmtree(out)
#         from .utils.data import split_triples, sort_triples, Triples
#         split_triples(
#             sort_triples(Triples(t.triple for t in _)),
#             chunk_size=nsplit_out)
#     else:
#         _.dump(str(out), 'text/turtle')
#     return out

#namdspaces include "ours"
#def replace_namespace

class triplesqueryname(str):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        self.query
    
    @property
    def query(self):
        from mapping.utils.queries import queries
        return getattr(queries.rules, self.name)


def extract_triples(
        ttl_or_dbdir: Path,
        *queries: Path|triplesqueryname,
        out: Path|None=Path('out.ttl')):
    ttl_or_dir = Path(ttl_or_dbdir)
    from pyoxigraph import Store
    if ttl_or_dir.suffix == '.ttl':
        from pyoxigraph import parse, Quad
        s = Store()
        s.bulk_extend(
            Quad(*t)
                for t in parse(ttl_or_dir, 'text/turtle'))
    else:
        assert(ttl_or_dir.is_dir())
        s = Store(ttl_or_dir)
    
    from pyoxigraph import serialize
    queriesargs = queries
    queries = []
    for q in queriesargs:
        if not Path(q).exists(): # it's some name
            queries.append(triplesqueryname(q).query)
        else:
            q = Path(q)
            assert(q.suffix == '.rq')
            q = q.read_text()
            queries.append(q)

    from mapping.utils.queries import select
    if not out:
        from io import BytesIO
        out = BytesIO()
    serialize(
        select(s, queries),
        out,
        'text/turtle')
    
    
    return out


if __name__ == '__main__':
    from fire import Fire
    Fire({'extract_triples': extract_triples})
