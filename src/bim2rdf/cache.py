"""persistent caching"""
try:
    from pathlib import Path
    dir = Path('.') / 'cache'
    dir.mkdir(exist_ok=True)
    (dir / '.gitignore').touch()
    (dir / '.gitignore').write_text('*')
    def cache(f, *p, dir=dir, **k):
        from cachier import cachier
        return cachier(*p, cache_dir=dir, **k)(f)
except:
    dir = None
    cache = lambda f, *p, **k: f

__all__ = ['cache', 'dir']