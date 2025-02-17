try:
    from pyprojroot import here
    cache_dir = here() / 'cache'
    cache_dir.mkdir(exist_ok=True)
    from 
except:
    cache_dir = None
    cache = lambda f: f

