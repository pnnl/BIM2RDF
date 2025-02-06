from fire import Fire
from pathlib import Path
def f(config: Path= Path('params.yaml')):
    config = Path(config)
    from yaml import safe_load
    config = safe_load(open(config))
    db = Path(config.pop('db'))
    from .engine import Run
    r = Run.from_path(db)
    _ = r.run(**config)
    return db
f = Fire(f)
exit(0)