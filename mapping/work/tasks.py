"""
tasks
"""
from pathlib import Path
from typing import Iterable, Self


class Stream:
    def __init__(self, meta) -> None:
        self.meta = meta

    @property
    def isnamed(self):
        if self.meta.name.startswith(Building.abbrev):
            return False
        else:
            return True
    @property
    def number(self):
        if not self.isnamed:
            for i,c in enumerate(self.meta.name):
                if c.isnumeric():
                    break
            _ = self.meta.name[i:]
            _ = int(_)
            return _


class Building:
    abbrev = 'bldg'

    def __init__(self, stream) -> None:
        self.stream = Stream(stream)

    @classmethod
    def streams(cls):
        from mapping.speckle import SpeckleGetter
        for _ in SpeckleGetter.get_streams():
            yield _
    @classmethod
    def s(cls) -> Iterable[Self]:
        yield from map(lambda s:cls(s), cls.streams())
    
    @classmethod
    def distribution(cls):
        _ = Path(__file__ ).parent / 'params.yaml'
        from yaml import safe_load
        _ = open(_)
        _ = safe_load(_)
        _ = _['distribution']
        from functools import cache
        @cache
        def distributionlist():
            assert(
                len({d['name'] for d in _})
                == 
                len({d['number'] for d in _}))
            return _
        return distributionlist()
    
    from functools import cached_property
    @cached_property
    def name(self):
        name = None
        if self.stream.isnamed:
            name = self.stream.meta.name
            assert(name in {d['name'] for d in self.distribution() } )
        else:
            for d in self.distribution():
                if d['number'] == self.stream.number:
                    name = d['name']
        assert(name)
        return name
    
    def __str__(self) -> str:
        return self.name

    @cached_property
    def number(self)->int:
        number = None
        if not self.stream.isnamed:
            number = self.stream.number
            assert(number in {d['number'] for d in self.distribution()}  )
        else:
            for d in self.distribution():
                if d['name'] == self.stream.meta.name:
                    number = d['number']
        assert(number)
        return number
        
    @cached_property
    def uri(self):
        from mapping.speckle import namespaces as sns
        for p, u in sns():
            if p == self.name:
                return u
    @property
    def prefix(self):
        return f"{self.abbrev}{self.number}"


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


def map_(f: Path):
    f = Path(f)
    if not (f.suffix in {'.yml', '.yaml'}):
        raise IOError('file needs to be yaml')
    _ = open(f)
    from yaml import safe_load
    p = safe_load(_) # params
    vn = p['run']['variation']
    for v in p['variations']:
        if v['name'] == vn: break
    if not (v['name'] == vn):
        raise ValueError('variation not found')

    stream = None
    for b in Building.s():
        if b.name == p['run']['building']:
            stream = b.stream.meta.name
    if not stream:
        raise ValueError('stream not found')
    from mapping.speckle import write_map
    return write_map(
        stream,
        branch_ids=v['branches'],
        rules=[Path(_) for _ in v['sparql_rules'] ],
        max_cycles=p['run']['max_cycles'],
        inference=v['inference'],
        validation=v['validation'],
        out=Path(p['run']['db']),
        )


from graphdb.tasks import upload_graph as upload_to_graphdb

if __name__ == '__main__':
    import logging
    logging.basicConfig(force=True) # force removes other loggers that got picked up.
    from engine.triples import logger
    logger.setLevel(logging.INFO)
    from mapping.engine import logger
    logger.setLevel(logging.INFO)
    from validation.engine import logger
    logger.setLevel(logging.INFO)

    from fire import Fire
    Fire({
        'map': map_,
        'extract_triples': extract_triples,
        'upload_to_graphdb': upload_to_graphdb,
        'copy_to_sharefolder': copy_to_sharefolder,
        })
