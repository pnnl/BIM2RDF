"""
distribution tasks
"""
from pathlib import Path
from typing import Iterable, Self


class Building:
    def __init__(self, name: str, ) -> None:
        self.name = name
    
    @classmethod
    def s(cls) -> Iterable[Self]:
        from mapping.speckle import SpeckleGetter
        for _ in SpeckleGetter.get_streams():
            yield cls(_.name)
    
    def __str__(self) -> str:
        return self.name
    
    from functools import cached_property

    @classmethod
    def get_numbers(cls):
        _ = Path(__file__ ).parent / 'params.yaml'
        from yaml import safe_load
        _ = open(_)
        _ = safe_load(_)
        _ = _['distribution']
        _ = {_['name']:_['number'] for _ in _}
        return _
    
    @cached_property
    def number(self)->int:
        _ = self.get_numbers()
        assert(
            len(_.keys())
               == 
            len(frozenset(_.values())) )
        return _[self.name]
    
    
    @cached_property
    def uri(self):
        from mapping.speckle import namespaces as sns
        for p, u in sns():
            if p == self.name:
                return u
    @property
    def prefix(self):
        return f"bdg{self.number}"



def namespaces():
    from mapping.utils.queries import namespaces as qns
    from ontologies import namespace
    bdgs = {b.name:b for b in Building.s()}
    for p, u in qns():
        if p in bdgs:
            yield namespace(bdgs[p].prefix, u)
        else:
            yield namespace(p, u)
        

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
        replace_bdgprefix=False,
        out: Path=Path('queried.ttl')):
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
    
    from io import BytesIO
    _ = BytesIO()
    from mapping.utils.queries import select
    serialize(
        select(s, queries),
        _,
        'text/turtle')
    _.seek(0)

    from rdflib import Graph
    _ = Graph().parse(_, format='text/turtle')


    if replace_bdgprefix:
        nss = namespaces
    else:
        from mapping.utils.queries import namespaces as nss
    for p,u in nss(): _.bind(p, u)

    _.serialize(out, format='text/turtle')
    return out


def syncdir():
    from pathlib import Path
    sharefolder = Path('Data-Driven Electrical Systems - PROJ-semanticinterop') / Path('generated')
    from platform import system
    if system().lower() == 'windows':
        return Path.home() / 'PNNL' / sharefolder
    else:
        return Path.home() / sharefolder


def copy_to_sharefolder(*srcs:Path,
        _sharefolder=syncdir(), dst_sharefolder=Path(),
        delete_dst=False,):
    dst = _sharefolder / Path(dst_sharefolder)
    if delete_dst and dst.exists():
        from shutil import rmtree
        rmtree(dst)

    for src in srcs:
        src = Path(src)
        if src.is_file():
            from shutil import copy
            copy(src, dst)
        else:
            assert(src.is_dir())
            from shutil import copytree as copy
            copy(src, dst, dirs_exist_ok=True)



from graphdb.tasks import upload_graph as upload_to_graphdb

if __name__ == '__main__':
    from fire import Fire
    Fire({
        'extract_triples': extract_triples,
        'upload_to_graphdb': upload_to_graphdb,
        'copy_to_sharefolder': copy_to_sharefolder,
        })
