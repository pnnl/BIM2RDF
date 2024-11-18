
def get_dir():
    from project import root
    from yaml import safe_load
    p = root / 'models' / 'params.yaml'
    p = open(p)
    p = safe_load(p)['run']
    dir = (
        root / 'models' / 'artifacts'
        / p['building'] / p['variation']
        /'cache')
    if not dir.exists():
        dir.mkdir()
    return dir


def get_cache(name, *p, dev=True, key=None, type='LRUCache', **k):
    if dev:
        fp = get_dir() / name
        from shelved_cache import PersistentCache
        import cachetools
        _ = getattr(cachetools, type)
        _ = PersistentCache(_, fp, *p, **k)
        if not key:
            _ = cachetools.cached(_)
        else:
            _ = cachetools.cached(_, key=key)
        return _
    else: # do nothing
        return lambda f: f 
