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







