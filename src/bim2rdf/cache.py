"""persistent caching"""
try:
    from cachier import cachier
    from pathlib import Path
    dir = Path('.') / 'cache'
    dir.mkdir(exist_ok=True)
    (dir / '.gitignore').touch()
    (dir / '.gitignore').write_text('*')
    def cache(f, *p, dir=dir, **k):
        return cachier(*p, cache_dir=dir, **k)(f)
except ModuleNotFoundError:
    dir = None
    cache = lambda f, *p, **k: f

__all__ = ['cache', 'dir']