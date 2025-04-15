
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

def run(params: Path= Path('params.yaml')):
    params = Path(params)
    from yaml import safe_load
    params: dict = safe_load(open(params))
    db = Path(params.pop(db_dir))
    r = Run.from_path(db)
    params.setdefault('project_id',     '')
    params.setdefault('project_name',   '')
    _ = r.run(**params)
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
run = attdoc(run)
from fire import Fire
run = Fire(run)
exit(0)
