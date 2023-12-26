from pathlib import Path
def get_store(ttl: Path=None, dir: Path=None,  overwrite=True):
    # dir: is pyoxigraph data dir
    from pyoxigraph import Store
    if overwrite:
        if Path(dir).exists():
            from shutil import rmtree
            rmtree(dir)

    if dir:
        try:
            s = Store(str(dir))
        except IOError:
            s = Store.read_only(str(dir))
    else:
        s = Store()
    
    if ttl:
        if overwrite:
            s.bulk_load(str(ttl), 'text/turtle')
    
    return s



if __name__ == '__main__':

    def extract_triples(
            ttl_or_dir: Path,
            *queries: Path|str):
        ttl_or_dir = Path(ttl_or_dir)
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
        for q in queries:
            q = Path(q)
            if not q.exists(): # it's some name
                qo = Path(f"{q}.ttl")
                assert(isinstance(q, str))
                from .queries import queries as querieso
                q = getattr(querieso.rules, q)
            else:
                assert(q.suffix == '.rq')
                qo = Path(*q.parts[:-1]) / (Path(q.parts[-1]).stem+'.ttl')
                q = q.read_text()
            
            _ = s.query(q,)
            serialize(_, qo ,'text/turtle')
    

    from fire import Fire
    Fire({'extract_triples': extract_triples})




