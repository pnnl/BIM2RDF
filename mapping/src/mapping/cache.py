
def get_dir():
    from project import root
    dir = root / 'mapping' / 'cache'
    if not dir.exists():
        dir.mkdir()
    return dir


def get_cache(name):
    ...