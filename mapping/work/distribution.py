# put distribution tasks here

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
