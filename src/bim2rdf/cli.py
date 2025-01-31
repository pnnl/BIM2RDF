from fire import Fire
from pathlib import Path
from .engine import Run
def f(
        db: Path,
        ontology:       Path,
        project_name:   str,
        model_name:     str,
        map_dirs = Run.defaults.mapdirs,
        MAX_NCYCLES=Run.defaults.MAX_NCYCLES,
            ):
    db = Path(db)
    ontology = Path(ontology)
    assert(ontology.exists())
    r = Run.from_path(db)
    map_dirs = [Path(d) for d in map_dirs]
    # https://smarie.github.io/python-makefun/#editing-a-signature TODO
    _ = r.run(
        ontology=ontology,
        project_name=project_name,
        model_name=model_name,
        map_dirs=map_dirs,
        MAX_NCYCLES=MAX_NCYCLES,)
    return db
f = Fire(f)

if __name__ == '__main__':
    f
