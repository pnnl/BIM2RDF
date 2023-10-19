
def get_dir():
    from project import root
    dir = root / 'mapping' / 'work' / 'cache'
    if not dir.exists():
        dir.mkdir()
    return dir


def get_cache(name, *, dev=True, key=None, type='LFUCache', maxsize=1_000_000, **k):
    if dev:
        fp = get_dir() / name
        from shelved_cache import PersistentCache
        import cachetools
        _ = getattr(cachetools, type)
        _ = PersistentCache(_, filename=fp, maxsize=maxsize, **k)
        if not key:
            _ = cachetools.cached(_)
        else:
            _ = cachetools.cached(_, key=key)
        return _
    else: # do nothing
        return lambda f: f 
