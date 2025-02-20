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
    
db_dir = 'db_dir'

def f(config: Path= Path('params.yaml')):
    config = Path(config)
    from yaml import safe_load
    config: dict = safe_load(open(config))
    db = Path(config.pop(db_dir))
    r = Run.from_path(db)
    config.setdefault('project_id',     '')
    config.setdefault('project_name',   '')
    _ = r.run(**config)
    return db
def attdoc(f):
    # bc it wont show up if it's not the first line
    defaults = Run.defaults
    _ = [atr for atr in dir(defaults) if not atr.startswith('_')]
    im = 'included_mappings'
    assert(im in _)
    pn = 'project_name'
    pi = 'project_id'
    def gt(atr):
        if im == atr:
            _ = '|'.join(defaults.included_mappings)
            return f'list[{_}]'
        return type(getattr(defaults, atr)).__name__
    _ = [f"{atr}:{gt(atr)}" for atr in _]
    _ = _ + [f"{db_dir}:list", pn, pi ]
    _ = '\n'.join(_)
    _ = f"""
    Required keys: {pn} OR {pi}.
    Optional config keys:
    {_}
    """
    f.__doc__ = _
    return f
from fire import Fire
f = attdoc(f)
f = Fire(f)
exit(0)
