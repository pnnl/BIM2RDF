from pathlib import Path
from .engine import Run
class Run(Run):
    
    @classmethod
    def from_path(cls, pth: Path|str, clear=True,):
        if isinstance(pth, str): pth = cls.Path(pth)
        if clear:
            if pth.exists():
                from shutil import rmtree
                rmtree(pth)
        return cls(cls.Store(str(pth)))
    

from fire import Fire

def f(config: Path= Path('params.yaml')):
    config = Path(config)
    from yaml import safe_load
    config = safe_load(open(config))
    db = Path(config.pop('db'))
    r = Run.from_path(db)
    _ = r.run(**config)
    return db
f = Fire(f)
exit(0)