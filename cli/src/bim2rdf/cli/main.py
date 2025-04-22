from pathlib import Path

pn, pi = 'project_name', 'project_id'
mn, mv = 'model_names', 'model_versions'
def run(
        params: Path= Path('params.yaml'),
        print_schema:bool=False):
    if print_schema: return schema()
    params = Path(params)
    from yaml import safe_load
    params: dict = safe_load(open(params))
    db_dir = Path(params['db'])
    if db_dir.exists():
        from shutil import rmtree
        rmtree(db_dir, ignore_errors=True)
    from pyoxigraph import Store
    params['db'] = Store(params['db'])
    from bim2rdf.core.engine import Run
    _ = Run(**params).run()
    return db_dir
def schema(): # TODO: may want to do pydantic-jsonschema
    from  bim2rdf.core.engine import Run, defaults
    def s(f):
        if f.name in dir(defaults):
            d = str(getattr(defaults, f.name))
        else:
            d = '*REQUIRED*'
        if f.name in {pn, pi}:
            d = d+' '+f'{pn} OR {pi}'
        elif f.name in {mn, mv}:
            d = d+' '+f'{mn} OR {mv}'
        d = ' = '+d
        if f.name == 'db':
            type = str(f.type.__name__)+' '+'dir'
        else: type = f.type.__name__
        return f"* {f.name}: {type} {d}"
    _ = '\n'.join(map(s, Run.__dataclass_fields__.values()))
    return _

from fire import Fire
from . import patch
from bim2rdf.ontologies.cli import main
main = Fire({'run':run, **{f'ontologies.{k}':v for k,v in main.items()} })
exit(0)
